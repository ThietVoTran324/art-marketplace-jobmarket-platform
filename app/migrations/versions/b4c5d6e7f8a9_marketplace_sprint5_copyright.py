"""marketplace sprint5 copyright

Revision ID: b4c5d6e7f8a9
Revises: a3b4c5d6e7f8
Create Date: 2026-08-08 21:10:00.000000
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "b4c5d6e7f8a9"
down_revision: Union[str, None] = "a3b4c5d6e7f8"
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
    "copyright_report_resolve",
    "copyright_report_dismiss",
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
    "job_report_create",
    "job_report_dismiss",
    "job_report_actioned",
    "company_suspend",
    "company_unsuspend",
)


def upgrade() -> None:
    op.drop_constraint("ck_audit_logs_action", "audit_logs", type_="check")
    op.create_check_constraint(
        "ck_audit_logs_action",
        "audit_logs",
        "action IN ('{}')".format("', '".join(NEW_AUDIT)),
    )

    op.add_column("pins", sa.Column("content_sha256", sa.String(length=64), nullable=True))

    op.add_column(
        "pin_listings",
        sa.Column(
            "attestation_accepted",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("false"),
        ),
    )
    op.add_column(
        "pin_listings",
        sa.Column("attestation_version", sa.String(length=50), nullable=True),
    )
    op.add_column(
        "pin_listings",
        sa.Column("attested_at", sa.TIMESTAMP(timezone=True), nullable=True),
    )

    op.create_table(
        "copyright_reports",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "reporter_user_id",
            sa.Integer(),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "pin_id",
            sa.Integer(),
            sa.ForeignKey("pins.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("reason", sa.String(length=500), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False, server_default="open"),
        sa.Column("admin_note", sa.String(length=500), nullable=True),
        sa.Column(
            "resolved_by_user_id",
            sa.Integer(),
            sa.ForeignKey("users.id", ondelete="SET NULL"),
            nullable=True,
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
            "status IN ('open', 'resolved', 'dismissed')",
            name="ck_copyright_reports_status",
        ),
    )
    op.create_index("ix_copyright_reports_pin_id", "copyright_reports", ["pin_id"])
    op.create_index("ix_copyright_reports_status", "copyright_reports", ["status"])

    op.create_table(
        "license_certificates",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "order_id",
            sa.Integer(),
            sa.ForeignKey("pin_orders.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "pin_id",
            sa.Integer(),
            sa.ForeignKey("pins.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "buyer_user_id",
            sa.Integer(),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "seller_user_id",
            sa.Integer(),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("license_type", sa.String(length=50), nullable=False, server_default="personal_use"),
        sa.Column("content_sha256", sa.String(length=64), nullable=True),
        sa.Column("certificate_code", sa.String(length=40), nullable=False),
        sa.Column("paid_at", sa.TIMESTAMP(timezone=True), nullable=False),
        sa.Column(
            "created_at",
            sa.TIMESTAMP(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.UniqueConstraint("order_id", name="uq_license_certificates_order_id"),
        sa.UniqueConstraint("certificate_code", name="uq_license_certificates_code"),
    )
    op.create_index("ix_license_certificates_buyer", "license_certificates", ["buyer_user_id"])
    op.create_index("ix_license_certificates_pin", "license_certificates", ["pin_id"])


def downgrade() -> None:
    op.drop_index("ix_license_certificates_pin", table_name="license_certificates")
    op.drop_index("ix_license_certificates_buyer", table_name="license_certificates")
    op.drop_table("license_certificates")
    op.drop_index("ix_copyright_reports_status", table_name="copyright_reports")
    op.drop_index("ix_copyright_reports_pin_id", table_name="copyright_reports")
    op.drop_table("copyright_reports")
    op.drop_column("pin_listings", "attested_at")
    op.drop_column("pin_listings", "attestation_version")
    op.drop_column("pin_listings", "attestation_accepted")
    op.drop_column("pins", "content_sha256")

    op.drop_constraint("ck_audit_logs_action", "audit_logs", type_="check")
    op.create_check_constraint(
        "ck_audit_logs_action",
        "audit_logs",
        "action IN ('{}')".format("', '".join(OLD_AUDIT)),
    )
