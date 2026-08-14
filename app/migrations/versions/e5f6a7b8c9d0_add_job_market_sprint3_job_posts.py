"""add job market sprint3 job_posts tables

Revision ID: e5f6a7b8c9d0
Revises: d4e5f6a7b8c9
Create Date: 2026-08-01 11:30:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "e5f6a7b8c9d0"
down_revision: Union[str, None] = "d4e5f6a7b8c9"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "job_posts",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "company_id",
            sa.Integer(),
            sa.ForeignKey("companies.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("title", sa.String(length=200), nullable=False),
        sa.Column("years_experience", sa.Integer(), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("requirements", sa.Text(), nullable=True),
        sa.Column("benefits", sa.Text(), nullable=True),
        sa.Column("salary_mode", sa.String(length=20), nullable=False),
        sa.Column("salary_min", sa.Integer(), nullable=True),
        sa.Column("salary_max", sa.Integer(), nullable=True),
        sa.Column(
            "currency",
            sa.String(length=3),
            nullable=False,
            server_default="VND",
        ),
        sa.Column(
            "status",
            sa.String(length=20),
            nullable=False,
            server_default="active",
        ),
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
            "salary_mode IN ('love_it', 'range')",
            name="ck_job_posts_salary_mode",
        ),
        sa.CheckConstraint(
            "currency IN ('VND', 'USD')",
            name="ck_job_posts_currency",
        ),
        sa.CheckConstraint(
            "status IN ('active', 'closed')",
            name="ck_job_posts_status",
        ),
        sa.CheckConstraint(
            "years_experience >= 0",
            name="ck_job_posts_years_experience",
        ),
    )
    op.create_index("ix_job_posts_company_status", "job_posts", ["company_id", "status"])
    op.create_index("ix_job_posts_status_created", "job_posts", ["status", "created_at"])

    op.create_table(
        "job_post_locations",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "job_post_id",
            sa.Integer(),
            sa.ForeignKey("job_posts.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "source_branch_id",
            sa.Integer(),
            sa.ForeignKey("company_branches.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("label", sa.String(length=100), nullable=True),
        sa.Column("address_line", sa.String(length=300), nullable=False),
        sa.Column("city", sa.String(length=100), nullable=True),
        sa.Column("country", sa.String(length=10), nullable=True),
        sa.Column(
            "created_at",
            sa.TIMESTAMP(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
    )
    op.create_index(
        "ix_job_post_locations_job_post_id",
        "job_post_locations",
        ["job_post_id"],
    )


def downgrade() -> None:
    op.drop_index("ix_job_post_locations_job_post_id", table_name="job_post_locations")
    op.drop_table("job_post_locations")
    op.drop_index("ix_job_posts_status_created", table_name="job_posts")
    op.drop_index("ix_job_posts_company_status", table_name="job_posts")
    op.drop_table("job_posts")
