"""job_posts add expires_at

Revision ID: c5d6e7f8a9b0
Revises: b4c5d6e7f8a9
Create Date: 2026-08-13 15:15:00.000000
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "c5d6e7f8a9b0"
down_revision: Union[str, None] = "b4c5d6e7f8a9"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "job_posts",
        sa.Column("expires_at", sa.TIMESTAMP(timezone=True), nullable=True),
    )
    # Backfill: 30 days from created_at for existing rows
    op.execute(
        sa.text(
            "UPDATE job_posts SET expires_at = created_at + interval '30 days' "
            "WHERE expires_at IS NULL"
        )
    )
    op.alter_column("job_posts", "expires_at", nullable=False)
    op.create_index("ix_job_posts_expires_at", "job_posts", ["expires_at"])
    op.create_index(
        "ix_job_posts_status_expires",
        "job_posts",
        ["status", "expires_at"],
    )


def downgrade() -> None:
    op.drop_index("ix_job_posts_status_expires", table_name="job_posts")
    op.drop_index("ix_job_posts_expires_at", table_name="job_posts")
    op.drop_column("job_posts", "expires_at")
