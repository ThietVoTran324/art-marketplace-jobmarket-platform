"""marketplace sprint1 media split

Revision ID: d0e1f2a3b4c5
Revises: c9d0e1f2a3b4
Create Date: 2026-08-08 11:15:00.000000
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "d0e1f2a3b4c5"
down_revision: Union[str, None] = "c9d0e1f2a3b4"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "pins",
        sa.Column("original_image", sa.String(length=200), nullable=True),
    )
    op.create_table(
        "pin_license_access",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("pin_id", sa.Integer(), nullable=False),
        sa.Column("order_id", sa.Integer(), nullable=True),
        sa.Column(
            "granted_at",
            sa.TIMESTAMP(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["pin_id"], ["pins.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id", "pin_id", name="uq_pin_license_access_user_pin"),
    )
    op.create_index(
        "ix_pin_license_access_pin_id",
        "pin_license_access",
        ["pin_id"],
    )


def downgrade() -> None:
    op.drop_index("ix_pin_license_access_pin_id", table_name="pin_license_access")
    op.drop_table("pin_license_access")
    op.drop_column("pins", "original_image")
