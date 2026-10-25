from integrations.core_banking.mock import MockCoreBankingProvider
from .models import Account


class AccountService:
    def __init__(self, provider=None):
        # Default to MockCoreBankingProvider during development/demo phases
        self.provider = provider or MockCoreBankingProvider()

    def get_customer_accounts(self, customer):
        return Account.objects.filter(customer=customer)

    def get_account_details_with_balance(self, account_id, customer):
        try:
            account = Account.objects.get(id=account_id, customer=customer)
        except Account.DoesNotExist:
            raise ValueError("Account not found or access denied.")

        # Authoritative balance retrieval from core banking provider
        balance_data = self.provider.get_account_balance(account.external_account_reference)

        return {
            "account_id": str(account.id),
            "account_number_masked": account.account_number_masked,
            "account_type": account.account_type,
            "currency": account.currency,
            "status": balance_data.get("status", account.status),
            "balance": balance_data.get("balance", 0.00),
            "external_reference": account.external_account_reference
        }
