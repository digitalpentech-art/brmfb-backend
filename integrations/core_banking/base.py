from abc import ABC, abstractmethod


class CoreBankingProvider(ABC):
    @abstractmethod
    def get_account_balance(self, external_account_reference: str) -> dict:
        """
        Retrieve authoritative account balance from core banking system.
        Returns: {"balance": float, "currency": str, "status": str}
        """
        pass

    @abstractmethod
    def verify_account_number(self, account_number: str) -> dict:
        """
        Verify account number existence and return account name.
        Returns: {"account_number": str, "account_name": str, "bank_code": str}
        """
        pass

    @abstractmethod
    def initiate_transfer(self, transfer_data: dict) -> dict:
        """
        Initiate fund transfer with core banking / interbank switch.
        Returns: {"external_reference": str, "status": str, "message": str}
        """
        pass
