import uuid
from .base import CoreBankingProvider


class MockCoreBankingProvider(CoreBankingProvider):
    def get_account_balance(self, external_account_reference: str) -> dict:
        # Simulate fetching authoritative balance from core banking mock system
        return {
            "balance": 250000.00,
            "currency": "NGN",
            "status": "ACTIVE",
            "external_reference": external_account_reference
        }

    def verify_account_number(self, account_number: str) -> dict:
        # Simulate account verification
        return {
            "account_number": account_number,
            "account_name": "Amina Borno Customer",
            "bank_code": "090561",  # BRMFB bank code mock
            "bank_name": "Borno Renaissance MFB"
        }

    def initiate_transfer(self, transfer_data: dict) -> dict:
        # Simulate transfer processing
        return {
            "external_reference": f"BRMFB-EXT-{uuid.uuid4().hex[:12].upper()}",
            "status": "SUCCESSFUL",
            "message": "Transfer processed successfully by mock core banking."
        }
