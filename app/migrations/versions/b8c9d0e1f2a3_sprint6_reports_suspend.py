"""sprint6 job reports company suspend

Revision ID: b8c9d0e1f2a3
Revises: a7b8c9d0e1f2
Create Date: 2026-08-04 19:45:00.000000
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "b8c9d0e1f2a3"
down_revision: Union[str, None] = "a7b8c9d0e1f2"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

NEW_AUDIT = (
    "admin_delete_pin",
    "admin_delete_comment",
    "role_assign",
    "role_revoke",
    "kyc_submit",
    "kyc_approve",
    "kyc_reject",
    "kyc_need_more_info",
    "work_exp_approve",
    "work_exp_reject",
    "job_report_create",
    "job_report_dismiss",
    "job_report_actioned",
    "company_suspend",
    "company_unsuspend",
)

OLD_AUDIT = (
    "admin_delete_pin",
    "admin_delete_comment",
    "role_assign",
    "role_revoke",
    "kyc_submit",
    "kyc_approve",
    "kyc_reject",
    "kyc_need_more_info",
    "work_exp_approve",
    "work_exp_reject",
)


def upgrade() -> None:
    op.drop_constraint("ck_audit_logs_action", "audit_logs", type_="check")
    op.create_check_constraint(
        "ck_audit_logs_action",
        "audit_logs",
        "action IN ('{}')".format("', '".join(NEW_AUDIT)),
    )

    op.add_column(
        "companies",
        sa.Column("suspend_reason", sa.Text(), nullable=True),
    )
    op.add_column(
        "companies",
        sa.Column("suspended_at", sa.TIMESTAMP(timezone=True), nullable=True),
    )

    op.create_table(
        "job_post_reports",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "job_post_id",
            sa.Integer(),
            sa.ForeignKey("job_posts.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "reporter_user_id",
            sa.Integer(),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("reason", sa.String(length=40), nullable=False),
        sa.Column("detail", sa.Text(), nullable=True),
        sa.Column("status", sa.String(length=20), nullable=False, server_default="open"),
        sa.Column("admin_note", sa.Text(), nullable=True),
        sa.Column(
            "resolved_by",
            sa.Integer(),
            sa.ForeignKey("users.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("resolved_at", sa.TIMESTAMP(timezone=True), nullable=True),
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
            "reason IN ('spam', 'scam', 'inappropriate', 'other')",
            name="ck_job_post_reports_reason",
        ),
        sa.CheckConstraint(
            "status IN ('open', 'dismissed', 'actioned')",
            name="ck_job_post_reports_status",
        ),
    )
    op.create_index(
        "ix_job_post_reports_job_post_id", "job_post_reports", ["job_post_id"]
    )
    op.create_index(
        "ix_job_post_reports_status_created",
        "job_post_reports",
        ["status", "created_at"],
    )
    op.create_index(
        "uq_job_post_reports_open_reporter_job",
        "job_post_reports",
        ["reporter_user_id", "job_post_id"],
        unique=True,
        postgresql_where=sa.text("status = 'open'"),
    )


def downgrade() -> None:
    op.drop_index(
        "uq_job_post_reports_open_reporter_job", table_name="job_post_reports"
    )
    op.drop_index("ix_job_post_reports_status_created", table_name="job_post_reports")
    op.drop_index("ix_job_post_reports_job_post_id", table_name="job_post_reports")
    op.drop_table("job_post_reports")
    op.drop_column("companies", "suspended_at")
    op.drop_column("companies", "suspend_reason")
    op.drop_constraint("ck_audit_logs_action", "audit_logs", type_="check")
    op.create_check_constraint(
        "ck_audit_logs_action",
        "audit_logs",
        "action IN ('{}')".format("', '".join(OLD_AUDIT)),
    )
