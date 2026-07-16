"""Shared wallet credit/debit and transfer — reuses Wallet + Transaction models."""

from decimal import Decimal

from django.db import transaction

from dashboard.models import Transaction, Wallet


class WalletError(Exception):
    pass


def _get_wallet(user):
    wallet, _ = Wallet.objects.select_for_update().get_or_create(user=user)
    return wallet


@transaction.atomic
def credit_debit_wallet(user, amount, txn_type, description=""):
    """
    Adjust a single user's wallet and log one Transaction.
    txn_type: "Credit" or "Debit"
    """
    amount = Decimal(amount)
    if amount <= 0:
        raise WalletError("Amount must be greater than zero.")
    if txn_type not in ("Credit", "Debit"):
        raise WalletError("Invalid transaction type.")

    wallet = _get_wallet(user)
    if txn_type == "Credit":
        wallet.balance += amount
    else:
        if wallet.balance < amount:
            raise WalletError("Insufficient wallet balance.")
        wallet.balance -= amount
    wallet.save(update_fields=["balance"])

    Transaction.objects.create(
        user=user,
        transaction_type=txn_type,
        amount=amount,
        balance_after_transaction=wallet.balance,
        description=description or "",
    )
    return wallet


@transaction.atomic
def transfer_wallet(from_user, to_user, amount, debit_description=None, credit_description=None):
    """Debit from_user and credit to_user with two Transaction rows."""
    amount = Decimal(amount)
    if amount <= 0:
        raise WalletError("Amount must be greater than zero.")

    from_wallet = _get_wallet(from_user)
    to_wallet = _get_wallet(to_user)

    if from_wallet.balance < amount:
        raise WalletError(
            f"Insufficient wallet balance. Current balance is ₹{from_wallet.balance}."
        )

    from_wallet.balance -= amount
    to_wallet.balance += amount
    from_wallet.save(update_fields=["balance"])
    to_wallet.save(update_fields=["balance"])

    Transaction.objects.create(
        user=from_user,
        amount=amount,
        transaction_type="Debit",
        balance_after_transaction=from_wallet.balance,
        description=debit_description
        or f"Transferred to: {to_user.full_name or to_user.email}",
    )
    Transaction.objects.create(
        user=to_user,
        amount=amount,
        transaction_type="Credit",
        balance_after_transaction=to_wallet.balance,
        description=credit_description
        or f"Received from: {from_user.full_name or from_user.email}",
    )
    return from_wallet, to_wallet
