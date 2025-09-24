from server.extensions import db
from datetime import datetime
from sqlalchemy import Column, Integer, DateTime, String

# ------------------------------------------------------------


class User(db.Model):
    """User DB model"""

    id = Column(Integer, primary_key=True)
    email = Column(String(20), unique=True, nullable=False)
    password_hash = Column(String(120), nullable=False)
    created_at = Column(DateTime, default=datetime.now)