from abc import ABC, abstractmethod
import os
import requests
from server.utils.logger import logger

# --------------------------------------


class PaymentService(ABC):
    """Base class for all payment gateways."""

    @abstractmethod
    def initialize_charge(self, **kwargs):
        """Initialize payment charge"""
        pass

    @abstractmethod
    def verify_payment(self, reference):
        """Verify payment status"""
        pass

    @abstractmethod
    def submit_otp(self, otp, reference):
        """Submit OTP for payment authorization"""
        pass

    @abstractmethod
    def charge(self, **kwargs):
        """Handle direct charges (card/bank/account)."""
        pass


class PaystackService(PaymentService):
    """Payment initialization and verification for Paystack charge"""

    def __init__(self):
        # Paystack secret key from environment
        self.secret_key = os.getenv("PAYSTACK_SECRET_KEY")
        # Base URL for Paystack API
        self.base_url = os.getenv("PAYSTACK_BASE_URL", "https://api.paystack.co")

    def initialize_charge(self, email, amount, metadata=None):
        """
        Initialize a transaction with Paystack.
        Amount should be in kobo. Email is required.
        """
        url = f"{self.base_url}/transaction/initialize"
        headers = {
            "Authorization": f"Bearer {self.secret_key}",
            "Content-type": "application/json",
        }

        payload = {"email": email, "amount": amount, "metadata": metadata or {}}
        logger.info("Initializing Paystack charge", extra_info={"email": email, "amount": amount})
        resp = requests.post(url=url, json=payload, headers=headers)
        return resp.json()

    def verify_payment(self, reference):
        """
        Verify transaction status by its reference.
        """
        url = f"{self.base_url}/transaction/verify/{reference}"
        headers = {"Authorization": f"Bearer {self.secret_key}"}
        # GET request for verification per Paystack docs
        logger.info("Verifying Paystack payment", extra_info={"reference": reference})
        resp = requests.get(url=url, headers=headers)

        return resp.json()

    def submit_otp(self, otp, reference):
        """
        Submit OTP to authorize a charge.
        Typically used in the 'no-redirect' flow.
        """
        url = f"{self.base_url}/charge/submit_otp"
        headers = {
            "Authorization": f"Bearer {self.secret_key}",
            "Content-type": "application/json",
        }

        payload = {"otp": otp, "reference": reference}
        logger.info("Submitting Paystack OTP", extra_info={"reference": reference})
        resp = requests.post(url=url, json=payload, headers=headers)
        return resp.json()

    def charge(self, email, amount, bank=None, card=None, metadata=None):
        """
        Direct charge for card or bank account.
        This is the entry point for 'no-redirect' flows.
        """
        url = f"{self.base_url}/charge"
        headers = {
            "Authorization": f"Bearer {self.secret_key}",
            "Content-type": "application/json",
        }

        payload = {
            "email": email,
            "amount": amount,
            "metadata": metadata or {}
        }
        
        # Add bank or card details if provided
        if bank:
            payload["bank"] = bank
        if card:
            payload["card"] = card

        logger.info("Direct charging Paystack", extra_info={"email": email, "amount": amount})
        resp = requests.post(url=url, json=payload, headers=headers)
        return resp.json()


class MoniepointService(PaymentService):
    """Payment initialization and verification for Moniepoint charge"""

    def __init__(self):
        # Moniepoint secret key from environment
        self.secret_key = os.getenv("MONIEPOINT_SECRET_KEY")
        # Base URL for Moniepoint API
        self.base_url = os.getenv("MONIEPOINT_BASE_URL", "https://api.moniepoint.com/v1")

    def initialize_charge(self, email, amount, metadata=None):
        """
        Initialize a transaction with Moniepoint.
        """
        url = f"{self.base_url}/payments/initialize"
        headers = {
            "Authorization": f"Bearer {self.secret_key}",
            "Content-type": "application/json",
        }

        # Moniepoint specific payload structure (Simulated)
        payload = {
            "customerEmail": email,
            "amount": amount,
            "metaData": metadata or {},
            "currency": "NGN"
        }
        logger.info("Initializing Moniepoint charge", extra_info={"email": email, "amount": amount})
        resp = requests.post(url=url, json=payload, headers=headers)
        return resp.json()

    def verify_payment(self, reference):
        """
        Verify Moniepoint transaction status.
        """
        url = f"{self.base_url}/payments/verify/{reference}"
        headers = {"Authorization": f"Bearer {self.secret_key}"}
        logger.info("Verifying Moniepoint payment", extra_info={"reference": reference})
        resp = requests.get(url=url, headers=headers)

        return resp.json()

    def submit_otp(self, otp, reference):
        """
        Submit OTP for Moniepoint (Simulated endpoint).
        """
        url = f"{self.base_url}/payments/submit-otp"
        headers = {
            "Authorization": f"Bearer {self.secret_key}",
            "Content-type": "application/json",
        }

        payload = {"otp": otp, "transactionReference": reference}
        resp = requests.post(url=url, json=payload, headers=headers)
        return resp.json()

    def charge(self, email, amount, bank=None, card=None, metadata=None):
        """
        Direct charge for Moniepoint (Simulated).
        """
        url = f"{self.base_url}/payments/charge"
        headers = {
            "Authorization": f"Bearer {self.secret_key}",
            "Content-type": "application/json",
        }

        payload = {
            "email": email,
            "amount": amount,
            "metadata": metadata or {}
        }
        
        if bank:
            payload["bankDetails"] = bank
        if card:
            payload["cardDetails"] = card

        logger.info("Direct charging Moniepoint", extra_info={"email": email, "amount": amount})
        resp = requests.post(url=url, json=payload, headers=headers)
        return resp.json()