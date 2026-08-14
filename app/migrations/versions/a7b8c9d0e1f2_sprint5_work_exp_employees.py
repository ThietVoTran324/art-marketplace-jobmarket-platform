"""sprint5 work-exp company link employees heads

Revision ID: a7b8c9d0e1f2
Revises: f6a7b8c9d0e1
Create Date: 2026-08-01 21:20:00.000000
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "a7b8c9d0e1f2"
down_revision: Union[str, None] = "f6a7b8c9d0e1"
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
        sa.Column(
            "employees_public",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("true"),
        ),
    )

    op.add_column(
        "work_experiences",
        sa.Column(
            "company_id",
            sa.Integer(),
            sa.ForeignKey("companies.id", ondelete="SET NULL"),
            nullable=True,
        ),
    )
    op.drop_constraint("ck_work_experiences_status", "work_experiences", type_="check")
    op.create_check_constraint(
        "ck_work_experiences_status",
        "work_experiences",
        "status IN ('pending', 'approved', 'rejected')",
    )
    op.create_index(
        "ix_work_experiences_company_status",
        "work_experiences",
        ["company_id", "status"],
    )
    op.create_index(
        "ix_work_experiences_user_company",
        "work_experiences",
        ["user_id", "company_id"],
    )

    op.create_table(
        "company_employee_heads",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "company_id",
            sa.Integer(),
            sa.ForeignKey("companies.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "user_id",
            sa.Integer(),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("title", sa.String(length=100), nullable=False),
        sa.Column("note", sa.Text(), nullable=True),
        sa.Column("sort_order", sa.Integer(), nullable=False, server_default="0"),
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
        sa.UniqueConstraint(
            "company_id", "user_id", name="uq_company_employee_heads_company_user"
        ),
    )
    op.create_index(
        "ix_company_employee_heads_company_id",
        "company_employee_heads",
        ["company_id"],
    )


def downgrade() -> None:
    op.drop_index("ix_company_employee_heads_company_id", table_name="company_employee_heads")
    op.drop_table("company_employee_heads")
    op.drop_index("ix_work_experiences_user_company", table_name="work_experiences")
    op.drop_index("ix_work_experiences_company_status", table_name="work_experiences")
    op.drop_constraint("ck_work_experiences_status", "work_experiences", type_="check")
    op.create_check_constraint(
        "ck_work_experiences_status",
        "work_experiences",
        "status IN ('pending', 'approved')",
    )
    op.drop_column("work_experiences", "company_id")
    op.drop_column("companies", "employees_public")
    op.drop_constraint("ck_audit_logs_action", "audit_logs", type_="check")
    op.create_check_constraint(
        "ck_audit_logs_action",
        "audit_logs",
        "action IN ('{}')".format("', '".join(OLD_AUDIT)),
    )
