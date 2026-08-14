"""marketplace sprint4 orders sepay

Revision ID: a3b4c5d6e7f8
Revises: f2a3b4c5d6e7
Create Date: 2026-08-08 21:00:00.000000
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "a3b4c5d6e7f8"
down_revision: Union[str, None] = "f2a3b4c5d6e7"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "pin_orders",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("buyer_user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("seller_user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("pin_id", sa.Integer(), sa.ForeignKey("pins.id", ondelete="CASCADE"), nullable=False),
        sa.Column(
            "listing_id",
            sa.Integer(),
            sa.ForeignKey("pin_listings.id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column("price_minor", sa.Integer(), nullable=False),
        sa.Column("currency", sa.String(length=10), nullable=False),
        sa.Column("charge_amount_vnd", sa.Integer(), nullable=False),
        sa.Column("payment_code", sa.String(length=40), nullable=False),
        sa.Column("provider", sa.String(length=30), nullable=False, server_default="sepay"),
        sa.Column("status", sa.String(length=20), nullable=False, server_default="pending"),
        sa.Column("commission_percent", sa.Float(), nullable=True),
        sa.Column("commission_minor", sa.Integer(), nullable=True),
        sa.Column("seller_net_minor", sa.Integer(), nullable=True),
        sa.Column("payout_status", sa.String(length=20), nullable=False, server_default="pending"),
        sa.Column("expires_at", sa.TIMESTAMP(timezone=True), nullable=False),
        sa.Column("paid_at", sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column(
            "created_at",
            sa.TIMESTAMP(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column(
            "updated_at",
            sa.TIMESTAMP(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.CheckConstraint(
            "status IN ('pending', 'paid', 'failed', 'cancelled')",
            name="ck_pin_orders_status",
        ),
        sa.CheckConstraint("currency IN ('USD', 'VND')", name="ck_pin_orders_currency"),
        sa.CheckConstraint("price_minor > 0", name="ck_pin_orders_price_minor"),
        sa.CheckConstraint("charge_amount_vnd > 0", name="ck_pin_orders_charge_vnd"),
        sa.CheckConstraint(
            "payout_status IN ('pending', 'manual', 'skipped')",
            name="ck_pin_orders_payout_status",
        ),
        sa.UniqueConstraint("payment_code", name="uq_pin_orders_payment_code"),
    )
    op.create_index("ix_pin_orders_buyer_status", "pin_orders", ["buyer_user_id", "status"])
    op.create_index("ix_pin_orders_pin_status", "pin_orders", ["pin_id", "status"])
    op.create_index("ix_pin_orders_expires_at", "pin_orders", ["expires_at"])

    op.create_table(
        "payment_events",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("provider", sa.String(length=30), nullable=False),
        sa.Column("provider_event_id", sa.String(length=80), nullable=False),
        sa.Column(
            "order_id",
            sa.Integer(),
            sa.ForeignKey("pin_orders.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column(
            "payload",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default=sa.text("'{}'::jsonb"),
        ),
        sa.Column(
            "processed_at",
            sa.TIMESTAMP(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.UniqueConstraint(
            "provider", "provider_event_id", name="uq_payment_events_provider_event"
        ),
    )
    op.create_index("ix_payment_events_order_id", "payment_events", ["order_id"])

    op.create_foreign_key(
        "fk_pin_license_access_order_id",
        "pin_license_access",
        "pin_orders",
        ["order_id"],
        ["id"],
        ondelete="SET NULL",
    )


def downgrade() -> None:
    op.drop_constraint(
        "fk_pin_license_access_order_id", "pin_license_access", type_="foreignkey"
    )
    op.drop_index("ix_payment_events_order_id", table_name="payment_events")
    op.drop_table("payment_events")
    op.drop_index("ix_pin_orders_expires_at", table_name="pin_orders")
    op.drop_index("ix_pin_orders_pin_status", table_name="pin_orders")
    op.drop_index("ix_pin_orders_buyer_status", table_name="pin_orders")
    op.drop_table("pin_orders")
