"""track recurring occurrence date on transactions

Revision ID: 097_001
Revises: 098_001
Create Date: 2026-10-13 13:30:00.000000
"""

from alembic import op


revision = "097_001"
down_revision = "098_001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # This migration previously used revision 097. Databases stamped with that
    # revision may already have the column and index.
    op.execute(
        "ALTER TABLE transactions "
        "ADD COLUMN IF NOT EXISTS recurring_occurrence_date DATE"
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_transactions_recurring_occurrence_date "
        "ON transactions (recurring_occurrence_date)"
    )


def downgrade() -> None:
    op.drop_index("ix_transactions_recurring_occurrence_date", "transactions")
    op.drop_column("transactions", "recurring_occurrence_date")
