import os
from dotenv import load_dotenv

load_dotenv()

# ----------------------------------------------------------------------------------------


class Config:
    """Server configuration"""

    SWAGGER = {"title": "Payment Orchestration API", "uiversion": 3, "openapi": "3.0.2"}
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "")

    # SQLALCHEMY
    SQLALCHEMY_DATABASE_URI = "sqlite:///db.sqlite3"
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Paystack
    PAYSTACK_SECRET_KEY = os.getenv("PAYSTACK_SECRET_KEY")
    PAYSTACK_PAYMENT_CHARGE_ENDPOINT = os.getenv("PAYSTACK_PAYMENT_CHARGE_ENDPOINT")

    # Moniepoint
    FLUTTERWAVE_SECRET_KEY = os.getenv("FLUTTERWAVE_SECRET_KEY")
    FLUTTERWAVE_PAYMENT_CHARGE_ENDPOINT = os.getenv(
        "FLUTTERWAVE_PAYMENT_CHARGE_ENDPOINT"
    )
