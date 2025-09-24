from server.models.user_model import User
from server.extensions import db
from server.utils.security import hash_password, verify_password
from server.utils.to_dict import to_dict

# ---------------------------------------------------------


def register_user(email, password):
    """Register user"""

    # User already exist
    if User.query.filter_by(email=email).first():
        return None

    userObj = User(email=email, password_hash=hash_password(password))
    db.session.add(userObj)
    db.session.commit()

    return to_dict(userObj)


def authenticated_user(email, password):
    """authenticate user"""
    user = User.query.filter_by(email=email).first()

    if user and verify_password(password, user.password_hash):
        return user
    return None