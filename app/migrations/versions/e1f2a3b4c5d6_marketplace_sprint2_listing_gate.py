"""marketplace sprint2 listing gate

Revision ID: e1f2a3b4c5d6
Revises: d0e1f2a3b4c5
Create Date: 2026-08-08 13:30:00.000000
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "e1f2a3b4c5d6"
down_revision: Union[str, None] = "d0e1f2a3b4c5"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "seller_payment_methods",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("method_type", sa.String(length=50), nullable=False),
        sa.Column("display_name", sa.String(length=100), nullable=False),
        sa.Column("account_identifier", sa.String(length=200), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column(
            "created_at",
            sa.TIMESTAMP(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.CheckConstraint(
            "method_type IN ('bank', 'e_wallet')",
            name="ck_seller_payment_methods_type",
        ),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_seller_payment_methods_user_id",
        "seller_payment_methods",
        ["user_id"],
    )

    op.create_table(
        "pin_listings",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("pin_id", sa.Integer(), nullable=False),
        sa.Column("seller_user_id", sa.Integer(), nullable=False),
        sa.Column(
            "license_type",
            sa.String(length=50),
            nullable=False,
            server_default="personal_use",
        ),
        sa.Column("price_minor", sa.Integer(), nullable=False),
        sa.Column(
            "currency",
            sa.String(length=10),
            nullable=False,
            server_default="USD",
        ),
        sa.Column(
            "status",
            sa.String(length=20),
            nullable=False,
            server_default="listed",
        ),
        sa.Column(
            "created_at",
            sa.TIMESTAMP(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.TIMESTAMP(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.CheckConstraint(
            "license_type IN ('personal_use')",
            name="ck_pin_listings_license_type",
        ),
        sa.CheckConstraint("price_minor > 0", name="ck_pin_listings_price_minor"),
        sa.CheckConstraint("currency IN ('USD', 'VND')", name="ck_pin_listings_currency"),
        sa.CheckConstraint("status IN ('listed', 'unlisted')", name="ck_pin_listings_status"),
        sa.ForeignKeyConstraint(["pin_id"], ["pins.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["seller_user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("pin_id", name="uq_pin_listings_pin_id"),
    )
    op.create_index(
        "ix_pin_listings_seller_status",
        "pin_listings",
        ["seller_user_id", "status"],
    )
    op.create_index("ix_pin_listings_status", "pin_listings", ["status"])


def downgrade() -> None:
    op.drop_index("ix_pin_listings_status", table_name="pin_listings")
    op.drop_index("ix_pin_listings_seller_status", table_name="pin_listings")
    op.drop_table("pin_listings")
    op.drop_index("ix_seller_payment_methods_user_id", table_name="seller_payment_methods")
    op.drop_table("seller_payment_methods")
