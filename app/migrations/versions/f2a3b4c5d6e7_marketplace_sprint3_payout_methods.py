"""marketplace sprint3 payout methods

Revision ID: f2a3b4c5d6e7
Revises: e1f2a3b4c5d6
Create Date: 2026-08-08 20:35:00.000000
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "f2a3b4c5d6e7"
down_revision: Union[str, None] = "e1f2a3b4c5d6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "seller_payment_methods",
        sa.Column("bank_name", sa.String(length=120), nullable=True),
    )
    op.add_column(
        "seller_payment_methods",
        sa.Column("account_holder", sa.String(length=120), nullable=True),
    )
    op.add_column(
        "seller_payment_methods",
        sa.Column(
            "is_primary",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("false"),
        ),
    )
    # First active method per user becomes primary
    op.execute(
        """
        UPDATE seller_payment_methods spm
        SET is_primary = true
        WHERE spm.id IN (
            SELECT DISTINCT ON (user_id) id
            FROM seller_payment_methods
            WHERE is_active = true
            ORDER BY user_id, id ASC
        )
        """
    )


def downgrade() -> None:
    op.drop_column("seller_payment_methods", "is_primary")
    op.drop_column("seller_payment_methods", "account_holder")
    op.drop_column("seller_payment_methods", "bank_name")
