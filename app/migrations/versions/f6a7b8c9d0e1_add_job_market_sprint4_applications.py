"""add job market sprint4 applications + updates metadata

Revision ID: f6a7b8c9d0e1
Revises: e5f6a7b8c9d0
Create Date: 2026-08-01 21:10:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "f6a7b8c9d0e1"
down_revision: Union[str, None] = "e5f6a7b8c9d0"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "updates",
        sa.Column("metadata", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
    )

    op.create_table(
        "job_applications",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "job_post_id",
            sa.Integer(),
            sa.ForeignKey("job_posts.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "applicant_user_id",
            sa.Integer(),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "status",
            sa.String(length=20),
            nullable=False,
            server_default="submitted",
        ),
        sa.Column("cover_note", sa.Text(), nullable=True),
        sa.Column("cover_original_filename", sa.String(length=255), nullable=True),
        sa.Column("cover_stored_name", sa.String(length=255), nullable=True),
        sa.Column("cover_content_type", sa.String(length=100), nullable=True),
        sa.Column("cover_size_bytes", sa.Integer(), nullable=True),
        sa.Column("cv_source", sa.String(length=20), nullable=False),
        sa.Column(
            "source_cv_id",
            sa.Integer(),
            sa.ForeignKey("user_cvs.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("cv_original_filename", sa.String(length=255), nullable=False),
        sa.Column("cv_stored_name", sa.String(length=255), nullable=False),
        sa.Column("cv_content_type", sa.String(length=100), nullable=False),
        sa.Column("cv_size_bytes", sa.Integer(), nullable=False),
        sa.Column("viewed_at", sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column("decided_at", sa.TIMESTAMP(timezone=True), nullable=True),
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
            "status IN ('submitted', 'viewed', 'rejected', 'passed')",
            name="ck_job_applications_status",
        ),
        sa.CheckConstraint(
            "cv_source IN ('tab', 'oneshot')",
            name="ck_job_applications_cv_source",
        ),
    )
    op.create_index(
        "ix_job_applications_job_created",
        "job_applications",
        ["job_post_id", "created_at"],
    )
    op.create_index(
        "ix_job_applications_applicant_job",
        "job_applications",
        ["applicant_user_id", "job_post_id"],
    )
    op.create_index(
        "ix_job_applications_job_status",
        "job_applications",
        ["job_post_id", "status"],
    )
    op.create_index(
        "uq_job_applications_open",
        "job_applications",
        ["applicant_user_id", "job_post_id"],
        unique=True,
        postgresql_where=sa.text("status IN ('submitted', 'viewed')"),
    )


def downgrade() -> None:
    op.drop_index("uq_job_applications_open", table_name="job_applications")
    op.drop_index("ix_job_applications_job_status", table_name="job_applications")
    op.drop_index("ix_job_applications_applicant_job", table_name="job_applications")
    op.drop_index("ix_job_applications_job_created", table_name="job_applications")
    op.drop_table("job_applications")
    op.drop_column("updates", "metadata")
