from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from server.services.transaction_service import (
    create_transaction,
    list_customer_transactions,
    get_transaction_by_gateway_ref,
    update_transaction_status,
)
from server.models.user_model import User
from server.services.payment_service import PaystackService

# ------------------------------------------------------------------------------------------


txn_bp = Blueprint("transaction", __name__)
paystack = PaystackService()


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

    user = User.query.get(customer_id)

    # Store pending transaction in DB
    txn = create_transaction(
        amount=data["amount"],
        gateway="paystack",
        customer_id=customer_id,
        txn_metadata=data.get("txn_metadata"),
    )

    # Initialize charge with Paystack
    paystack_resp = paystack.initialize_charge(
        email=user.email,
        amount=data["amount"],
        metadata={"internal_gateway_ref": txn.gateway_ref},
    )

    return jsonify(
        {
            "data": {
                "internal_gateway_ref": txn.gateway_ref,
                "gateway_resp": paystack_resp,
            },
            "msg": "Payment initialization successful",
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

    # Fetch transaction from DB and check ownership
    txn = get_transaction_by_gateway_ref(reference)
    if not txn or txn.customer_id != customer_id:
        return jsonify({"error": "Transaction not found", "status": 404})

    paystack_resp = paystack.verify_payment(reference=reference)

    gateway_status = paystack_resp.get("data", {}).get("status")

    if gateway_status:
        update_transaction_status(reference, gateway_status)

    return jsonify(
        {
            "data": {
                "internal_gateway_ref": txn.gateway_ref,
                "gateway_status": gateway_status,
                "gateway_response": paystack_resp,
            },
            "msg": "Payment verification returned successfully",
            "status": 200,
        }
    )