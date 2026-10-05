import uuid
from datetime import date, timedelta
from decimal import Decimal
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.app_clock import app_today
from app.models.account import Account
from app.services.fx_rate_service import convert


SPENDABLE_ACCOUNT_TYPES = ("checking", "savings")


async def _spendable_account_ids(
    session: AsyncSession,
    workspace_id: uuid.UUID,
    account_ids: Optional[list[uuid.UUID]] = None,
) -> list[uuid.UUID]:
    """Return open checking/savings account ids, respecting collection filters."""
    if account_ids is not None and len(account_ids) == 0:
        return []

    filters = [
        Account.workspace_id == workspace_id,
        Account.is_closed == False,
        Account.type.in_(SPENDABLE_ACCOUNT_TYPES),
    ]
    if account_ids:
        filters.append(Account.id.in_(account_ids))

    result = await session.execute(select(Account.id).where(*filters))
    return list(result.scalars().all())


async def get_projected_available_balance(
    session: AsyncSession,
    workspace_id: uuid.UUID,
    month_start: date,
    month_end: date,
    cutoff: date,
    primary_currency: str,
    account_ids: Optional[list[uuid.UUID]] = None,
) -> tuple[float, float, float]:
    """Compute current and projected available balance in primary currency.

    Available balance is intentionally narrower than net worth: it only covers
    open checking/savings accounts. The projection then applies future
    recurring rows plus pending/future forecast transactions through the end of
    the selected month.
    """
    spendable_ids = await _spendable_account_ids(session, workspace_id, account_ids)
    if not spendable_ids:
        return 0.0, 0.0, 0.0

    # Imported lazily to keep this service independent while sharing the
    # dashboard's already-tested balance and forecast semantics.
    from app.services.dashboard_service import (
        _get_forecast_transactions,
        _get_recurring_projections,
        _total_balance_by_currency,
    )

    current_by_currency = await _total_balance_by_currency(
        session, workspace_id, cutoff, spendable_ids
    )
    projected_by_currency = dict(current_by_currency)

    today = app_today()
    if month_end > cutoff and month_end > today:
        projection_start = cutoff + timedelta(days=1)

        recurring_rows = await _get_recurring_projections(
            session,
            workspace_id,
            projection_start,
            month_end,
            spendable_ids,
            include_transfer_like=True,
        )
        for row in recurring_rows:
            signed = row["amount"] if row["type"] == "credit" else -row["amount"]
            projected_by_currency[row["currency"]] = (
                projected_by_currency.get(row["currency"], 0.0) + signed
            )

        forecast_rows = await _get_forecast_transactions(
            session,
            workspace_id,
            date.min,
            month_end,
            spendable_ids,
        )
        for tx in forecast_rows:
            if tx.is_ignored or (tx.category and tx.category.is_ignored):
                continue
            if (
                tx.account
                and tx.account.connection_id
                and tx.status == "pending"
                and tx.date <= today
                and tx.source != "recurring"
            ):
                continue
            account_currency = tx.account.currency if tx.account else tx.currency
            amount = (
                tx.amount
                if tx.currency == account_currency
                else (tx.amount_primary or tx.amount)
            )
            signed = amount if tx.type == "credit" else -amount
            projected_by_currency[account_currency] = (
                projected_by_currency.get(account_currency, 0.0) + float(signed)
            )

    async def total_primary(amounts: dict[str, float]) -> float:
        total = 0.0
        for currency, amount in amounts.items():
            converted, _ = await convert(
                session, Decimal(str(amount)), currency, primary_currency, cutoff
            )
            total += float(converted)
        return round(total, 2)

    available = await total_primary(current_by_currency)
    projected = await total_primary(projected_by_currency)
    return available, projected, round(projected - available, 2)
