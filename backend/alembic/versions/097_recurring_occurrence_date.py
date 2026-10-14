"""track recurring occurrence date on transactions

Revision ID: 097
Revises: 096
Create Date: 2026-10-13 13:30:00.000000
"""

from alembic import op
import sqlalchemy as sa


revision = "097"
down_revision = "096"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "transactions",
        sa.Column("recurring_occurrence_date", sa.Date(), nullable=True),
    )
    op.create_index(
        "ix_transactions_recurring_occurrence_date",
        "transactions",
        ["recurring_occurrence_date"],
    )


def downgrade() -> None:
    op.drop_index("ix_transactions_recurring_occurrence_date", "transactions")
    op.drop_column("transactions", "recurring_occurrence_date")
