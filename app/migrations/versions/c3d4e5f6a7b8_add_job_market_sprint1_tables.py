"""add job market sprint1 tables

Revision ID: c3d4e5f6a7b8
Revises: b2c3d4e5f6a7
Create Date: 2026-07-26 16:35:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "c3d4e5f6a7b8"
down_revision: Union[str, None] = "b2c3d4e5f6a7"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "work_experiences",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("company_name", sa.String(length=200), nullable=False),
        sa.Column("employment_type", sa.String(length=50), nullable=False),
        sa.Column("title", sa.String(length=200), nullable=False),
        sa.Column("location", sa.String(length=200), nullable=True),
        sa.Column("start_date", sa.Date(), nullable=False),
        sa.Column("end_date", sa.Date(), nullable=True),
        sa.Column("status", sa.String(length=20), nullable=False, server_default="pending"),
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
            "employment_type IN ('full-time', 'part-time', 'hybrid', 'outsourcing', 'collaborator')",
            name="ck_work_experiences_employment_type",
        ),
        sa.CheckConstraint(
            "status IN ('pending', 'approved')",
            name="ck_work_experiences_status",
        ),
    )
    op.create_index(
        "ix_work_experiences_user_start",
        "work_experiences",
        ["user_id", "start_date"],
    )

    op.create_table(
        "profile_credentials",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("kind", sa.String(length=50), nullable=False),
        sa.Column("title", sa.String(length=200), nullable=False),
        sa.Column("organization", sa.String(length=200), nullable=True),
        sa.Column("occurred_on", sa.Date(), nullable=True),
        sa.Column("description", sa.String(length=400), nullable=True),
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
            "kind IN ('education', 'licensing', 'award')",
            name="ck_profile_credentials_kind",
        ),
    )
    op.create_index(
        "ix_profile_credentials_user_kind",
        "profile_credentials",
        ["user_id", "kind"],
    )

    op.create_table(
        "user_cvs",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("original_filename", sa.String(length=255), nullable=False),
        sa.Column("stored_name", sa.String(length=255), nullable=False),
        sa.Column("content_type", sa.String(length=100), nullable=False),
        sa.Column("size_bytes", sa.Integer(), nullable=False),
        sa.Column(
            "created_at",
            sa.TIMESTAMP(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
    )
    op.create_index("ix_user_cvs_user_id", "user_cvs", ["user_id"])


def downgrade() -> None:
    op.drop_index("ix_user_cvs_user_id", table_name="user_cvs")
    op.drop_table("user_cvs")
    op.drop_index("ix_profile_credentials_user_kind", table_name="profile_credentials")
    op.drop_table("profile_credentials")
    op.drop_index("ix_work_experiences_user_start", table_name="work_experiences")
    op.drop_table("work_experiences")
