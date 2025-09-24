from server.extensions import db
from server.models.transaction_model import Transaction
import uuid

# ------------------------------------------------------


def generate_reference():
    return "txn_" + uuid.uuid4().hex[:10]


def create_transaction(amount, gateway, customer_id, txn_metadata=None):
    gateway_ref = generate_reference()
    txn = Transaction(
        gateway_ref=gateway_ref,
        amount=amount,
        gateway=gateway,
        status="pending",
        customer_id=customer_id,
        txn_metadata=txn_metadata or {},
    )
    db.session.add(txn)
    db.session.commit()
    return txn


def get_transaction_by_gateway_ref(gateway_ref):
    return Transaction.query.filter_by(gateway_ref=gateway_ref).first()


def list_customer_transactions(customer_id):
    return (
        Transaction.query.filter_by(customer_id=customer_id)
        .order_by(Transaction.created_at.desc())
        .all()
    )


def update_transaction_status(gateway_ref, status):
    txn = get_transaction_by_gateway_ref(gateway_ref)

    if txn:
        txn.status = status
        db.session.commit()

    return txn