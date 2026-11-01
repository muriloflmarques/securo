"""Restore stable account IDs after the local and upstream 097 revisions collided.

Revision ID: 098_001
Revises: 098

Some databases ran the loan-property migration while it was revision 097 on
its feature branch, before the upstream revision 097 (stable account IDs) was
merged. The loan-property migration became upstream revision 098, but those
databases were already stamped 097 and skipped the stable account ID migration.
"""

from alembic import op

revision = "098_001"
down_revision = "098"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        "ALTER TABLE accounts ADD COLUMN IF NOT EXISTS stable_external_id VARCHAR(255)"
    )


def downgrade() -> None:
    # Revision 097 owns this column on databases that ran the full chain.
    pass
