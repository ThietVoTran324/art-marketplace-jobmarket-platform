"""marketplace sprint0 0-market data

Revision ID: c9d0e1f2a3b4
Revises: b8c9d0e1f2a3
Create Date: 2026-08-08 10:55:00.000000
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "c9d0e1f2a3b4"
down_revision: Union[str, None] = "b8c9d0e1f2a3"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Dedup likes (keep min id)
    op.execute(
        """
        DELETE FROM likes a
        USING likes b
        WHERE a.pin_id IS NOT NULL
          AND a.pin_id = b.pin_id
          AND a.user_id = b.user_id
          AND a.id > b.id
        """
    )
    op.execute(
        """
        DELETE FROM likes a
        USING likes b
        WHERE a.comment_id IS NOT NULL
          AND a.comment_id = b.comment_id
          AND a.user_id = b.user_id
          AND a.id > b.id
        """
    )

    # Dedup subscriptions + remove self-follows
    op.execute(
        """
        DELETE FROM subscriptions a
        USING subscriptions b
        WHERE a.follower_id = b.follower_id
          AND a.following_id = b.following_id
          AND a.id > b.id
        """
    )
    op.execute("DELETE FROM subscriptions WHERE follower_id = following_id")

    op.add_column(
        "pins",
        sa.Column(
            "created_at",
            sa.TIMESTAMP(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
    )

    op.create_table(
        "pin_stats",
        sa.Column("pin_id", sa.Integer(), nullable=False),
        sa.Column(
            "view_count",
            sa.BigInteger(),
            server_default=sa.text("0"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.TIMESTAMP(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["pin_id"], ["pins.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("pin_id"),
    )
    op.execute(
        """
        INSERT INTO pin_stats (pin_id, view_count)
        SELECT id, 0 FROM pins
        ON CONFLICT DO NOTHING
        """
    )

    op.create_index(
        "uq_likes_user_pin",
        "likes",
        ["user_id", "pin_id"],
        unique=True,
        postgresql_where=sa.text("pin_id IS NOT NULL"),
    )
    op.create_index(
        "uq_likes_user_comment",
        "likes",
        ["user_id", "comment_id"],
        unique=True,
        postgresql_where=sa.text("comment_id IS NOT NULL"),
    )
    op.create_unique_constraint(
        "uq_subscriptions_follower_following",
        "subscriptions",
        ["follower_id", "following_id"],
    )
    op.create_check_constraint(
        "ck_subscriptions_no_self_follow",
        "subscriptions",
        "follower_id <> following_id",
    )


def downgrade() -> None:
    op.drop_constraint("ck_subscriptions_no_self_follow", "subscriptions", type_="check")
    op.drop_constraint("uq_subscriptions_follower_following", "subscriptions", type_="unique")
    op.drop_index("uq_likes_user_comment", table_name="likes")
    op.drop_index("uq_likes_user_pin", table_name="likes")
    op.drop_table("pin_stats")
    op.drop_column("pins", "created_at")
