from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from server.services.transaction_service import (
    create_transaction,
    list_customer_transactions,
    get_transaction_by_gateway_ref,
    update_transaction_status,
)
from server.models.user_model import User
from server.services.payment_service import PaystackService, MoniepointService
from server.utils.logger import logger

# ------------------------------------------------------------------------------------------


txn_bp = Blueprint("transaction", __name__)

# Service Registry for dynamic gateway selection
services = {
    "paystack": PaystackService(),
    "moniepoint": MoniepointService()
}



@txn_bp.route("/", methods=["POST"])
@jwt_required()
def create_txn():
    """
    Create a new transaction (Simulation)
    ---
    tags:
      - Transactions
    requestBody:
      required: true
      content:
        application/json:
          schema:
            type: object
            properties:
              amount:
                type: integer
              gateway:
                type: string
              txn_metadata:
                type: object
    responses:
      201:
        description: Transaction created
    """

    data = request.json
    customer_id = get_jwt_identity()
    txn = create_transaction(
        amount=data["amount"],
        gateway=data["gateway"],
        customer_id=customer_id,
        txn_metadata=["txn_metadata"],
    )
    data = {
        "gateway_ref": txn.gateway_ref,
        "status": txn.status,
        "amount": txn.amount,
        "gateway": txn.gateway,
        "created_at": txn.created_at.isoformat(),
    }
    return jsonify({"data": data, "message": "Transaction created", "status": 201})


@txn_bp.route("/", methods=["GET"])
@jwt_required()
def list_txns():
    """
    List transactions for the logged-in user
    ---
    tags:
        - Transactions
    responses:
        200:
            description: List of transactions
    """

    customer_id = get_jwt_identity()
    txns = list_customer_transactions(customer_id)
    data = [
        {
            "gateway_ref": t.gateway_ref,
            "amount": t.amount,
            "status": t.status,
            "gateway": t.gateway,
            "created_at": t.created_at.isoformat(),
        }
        for t in txns
    ]
    return jsonify({"data": data, "message": "List of transactions", "status": 201})


@txn_bp.route("/initiate", methods=["POST"])
@jwt_required()
def initiate_payment():
    """
    Initiate a Paystack payment charge
    ---
    tags:
      - Transactions
    requestBody:
      required: true
      content:
        application/json:
          schema:
            type: object
            properties:
              amount:
                type: integer
              metadata:
                type: object
    responses:
      200:
        description: Payment initialization response
    """

    data = request.json()
    customer_id = int(get_jwt_identity())
    gateway = data.get("gateway", "paystack")
    logger.info("Payment initiation started", extra_info={"customer_id": customer_id, "gateway": gateway, "amount": data["amount"]})
    
    # 0. Get the correct service
    payment_service = services.get(gateway)
    if not payment_service:
        logger.error("Unsupported gateway", extra_info={"gateway": gateway})
        return jsonify({"error": f"Unsupported gateway: {gateway}", "status": 400}), 400

    # Fetch user for email (required by Paystack and Moniepoint)
    user = User.query.get(customer_id)

    # 1. Store pending transaction in our database
    txn = create_transaction(
        amount=data["amount"],
        gateway=gateway,
        customer_id=customer_id,
        txn_metadata=data.get("txn_metadata"),
    )

    # 2. Check if this is a direct charge (no-redirect flow)
    # If card or bank info is provided, we use the charge endpoint
    bank = data.get("bank")
    card = data.get("card")

    if bank or card:
        # Initialize direct charge
        payment_resp = payment_service.charge(
            email=user.email,
            amount=data["amount"],
            bank=bank,
            card=card,
            metadata={"internal_gateway_ref": txn.gateway_ref},
        )
    else:
        # Standard initialization (returns authorization_url for redirect)
        payment_resp = payment_service.initialize_charge(
            email=user.email,
            amount=data["amount"],
            metadata={"internal_gateway_ref": txn.gateway_ref},
        )

    # 3. Update internal transaction status if response is immediate
    gateway_status = payment_resp.get("data", {}).get("status")
    if gateway_status:
        update_transaction_status(txn.gateway_ref, gateway_status)

    return jsonify(
        {
            "data": {
                "internal_gateway_ref": txn.gateway_ref,
                "gateway_resp": payment_resp,
            },
            "msg": "Payment initiation processed",
            "status": 200,
        }
    )



@txn_bp.route("/verify/<reference>", methods=["GET"])
@jwt_required()
def verify_payment(reference):
    """
    Verify payment via Paystack and update transaction status
    ---
    tags:
      - Transactions
    parameters:
      in: path
      name: reference
      required: true
      schema:
        type: string
    responses:
      200:
        description: Payment verification result
    """
    

    customer_id = int(get_jwt_identity())
    logger.info("Payment verification requested", extra_info={"reference": reference, "customer_id": customer_id})

    # Fetch transaction from DB and check ownership
    txn = get_transaction_by_gateway_ref(reference)
    if not txn or txn.customer_id != customer_id:
        logger.warning("Transaction not found or unauthorized access", extra_info={"reference": reference, "customer_id": customer_id})
        return jsonify({"error": "Transaction not found", "status": 404})

    # Get the correct service
    payment_service = services.get(txn.gateway)
    if not payment_service:
        return jsonify({"error": f"Unsupported gateway: {txn.gateway}", "status": 400}), 400

    payment_resp = payment_service.verify_payment(reference=reference)

    gateway_status = payment_resp.get("data", {}).get("status")

    if gateway_status:
        update_transaction_status(reference, gateway_status)

    return jsonify(
        {
            "data": {
                "internal_gateway_ref": txn.gateway_ref,
                "gateway_status": gateway_status,
                "gateway_response": payment_resp,
            },
            "msg": "Payment verification returned successfully",
            "status": 200,
        }
    )


@txn_bp.route("/submit-otp", methods=["POST"])
@jwt_required()
def submit_otp():
    """
    Submit OTP for a pending transaction
    ---
    tags:
      - Transactions
    requestBody:
      required: true
      content:
        application/json:
          schema:
            type: object
            properties:
              otp:
                type: string
              reference:
                type: string
    responses:
      200:
        description: OTP submission result
      404:
        description: Transaction not found or unauthorized
    """

    data = request.json
    otp = data.get("otp")
    reference = data.get("reference")
    customer_id = int(get_jwt_identity())
    logger.info("OTP submission requested", extra_info={"reference": reference, "customer_id": customer_id})

    # 1. Fetch transaction from DB and verify ownership
    txn = get_transaction_by_gateway_ref(reference)
    if not txn or txn.customer_id != customer_id:
        logger.warning("Transaction not found for OTP submission", extra_info={"reference": reference, "customer_id": customer_id})
        return jsonify({"error": "Transaction not found or unauthorized", "status": 404}), 404

    # 2. Get the correct service
    payment_service = services.get(txn.gateway)
    if not payment_service:
        return jsonify({"error": f"Unsupported gateway: {txn.gateway}", "status": 400}), 400

    # 3. Submit OTP via the service
    payment_resp = payment_service.submit_otp(otp=otp, reference=reference)
    
    gateway_status = payment_resp.get("data", {}).get("status")

    # 4. Update internal transaction status if the gateway provides one
    if gateway_status:
        update_transaction_status(reference, gateway_status)

    return jsonify(
        {
            "data": {
                "internal_gateway_ref": txn.gateway_ref,
                "gateway_status": gateway_status,
                "gateway_response": payment_resp,
            },
            "msg": "OTP submitted successfully",
            "status": 200,
        }
    )