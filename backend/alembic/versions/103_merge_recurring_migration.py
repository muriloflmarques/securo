"""Join the recurring occurrence migration with upstream revisions.

Revision ID: 103
Revises: 097_001, 102
"""

revision = "103"
down_revision = ("097_001", "102")
branch_labels = None
depends_on = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
