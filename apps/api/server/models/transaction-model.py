from server.extensions import db
from sqlalchemy.dialects.sqlite import JSON
from sqlalchemy import Column, Integer, DateTime, String
from datetime import datetime

# -------------------------------------------


class Transaction(db.Model):
    id = Column(Integer, primary_key=True)
    gateway_ref = Column(String(64), unique=True, nullable=False)  # Unique gateway ref
    amount = Column(Integer, nullable=False)
    gateway = Column(String(32), nullable=False)
    status = Column(
        String(10), nullable=False, unique=False, default="pending"
    )  # pending, failed, "success"
    txn_metadata = Column(JSON, nullable=True)  # Unstructured JSON data
    customer_id = Column(Integer, db.ForeignKey("user.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.now)