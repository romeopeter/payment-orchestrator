from flask import Blueprint, request, jsonify
from server.services.auth_service import register_user, authenticated_user
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from server.utils.to_dict import to_dict
from server.models.user_model import User

# -------------------------------------------------------


auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/register", methods=["POST"])
def register():
    """
    Register a new user
    ---
    tags:
      - Auth
    requestBody:
      required: true
      content:
        application/json:
          schema:
            type: object
            properties:
              email:
                type: string
              password:
                type: string
    responses:
      201:
        description: User registered
      400:
        description: User already exists
    """
    data = request.json
    user = register_user(data["email"], data["password"])
    if user is None:
        return jsonify({"message": "User already exist", "status": 400})
    return jsonify({"message": "User registered", "user": user, "status": 201})


@auth_bp.route("/login", methods=["POST"])
def login():
    """
    Login and retrieve JWT token
    ---
    tags:
      - Auth
    requestBody:
      required: true
      content:
        application/json:
          schema:
            type: object
            properties:
              email:
                type: string
              password:
                type: string
    responses:
      200:
        description: JWT token returned
      401:
        description: Invalid credentials
    """
    data = request.json
    user = authenticated_user(data["email"], data["password"])
    if not user:
        return jsonify({"error": "Invalid credentials", "status": 401})
    access_token = create_access_token(identity=str(user.id))
    return jsonify({"access_token": access_token, "status": 200})


@auth_bp.route("/me", methods=["GET"])
@jwt_required()
def profile():
    """Token(user) identity route"""
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)
    return jsonify({"user", to_dict(user)})