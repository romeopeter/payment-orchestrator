from abc import ABC, abstractmethod
import os
import requests


class PaymentService(ABC):
    """Base class for all payment gateways."""

    @abstractmethod
    def initialize_charge():
        """Start a payment charge."""

        pass

    @abstractmethod
    def verify_payment():
        """Verify payment status."""
        pass


class PaystackService(PaymentService):
    """Payment initialization and verification for Paystack charge"""

    def __init__(self):
        self.secret_key = os.getenv("PAYSTACK_SECRET_KEY")
        self.base_url = os.getenv("PAYSTACK_PAYMENT_CHARGE_ENDPOINT")

    def initialize_charge(self, email, amount, metadata=None):
        """
        Amount should be in kobo (i.e). Email is required by paystack for charge initialization.
        Metadata is optional.
        """

        url = f"{self.base_url}/transaction/initialize"  # Must confirm from API
        headers = {
            "Authorization": f"Bearer {self.secret_key}",
            "Content-type": "application/json",
        }

        payload = {"email": email, "amount": amount, "metadata": metadata or {}}
        resp = requests.post(url=url, json=payload, headers=headers)
        return resp.json()

    def verify_payment(self, reference):
        """
        Verify transaction by reference
        """

        url = f"{self.base_url}/transaction/verify{reference}"
        headers = {"Authorization": f"Bearer {self.secret_key}"}
        resp = requests.post(url=url, headers=headers)

        return resp.json()