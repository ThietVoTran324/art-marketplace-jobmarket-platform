"""add user_roles table with backfill

Revision ID: a1b2c3d4e5f6
Revises: d948933f5835
Create Date: 2026-07-25 14:15:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

from app.config import settings

revision: str = "a1b2c3d4e5f6"
down_revision: Union[str, None] = "d948933f5835"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "user_roles",
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("role", sa.String(length=50), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("user_id", "role"),
    )

    op.execute(
        sa.text(
            """
            INSERT INTO user_roles (user_id, role)
            SELECT id, 'artist' FROM users
            ON CONFLICT (user_id, role) DO NOTHING
            """
        )
    )

    bootstrap = settings.BOOTSTRAP_ADMIN_USERNAME
    if bootstrap:
        op.execute(
            sa.text(
                """
                INSERT INTO user_roles (user_id, role)
                SELECT id, 'admin' FROM users WHERE username = :username
                ON CONFLICT (user_id, role) DO NOTHING
                """
            ).bindparams(username=bootstrap)
        )


def downgrade() -> None:
    op.drop_table("user_roles")
