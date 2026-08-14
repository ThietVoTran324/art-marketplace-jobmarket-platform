"""add job market sprint2 companies kyc tables

Revision ID: d4e5f6a7b8c9
Revises: c3d4e5f6a7b8
Create Date: 2026-07-28 08:30:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "d4e5f6a7b8c9"
down_revision: Union[str, None] = "c3d4e5f6a7b8"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

KYC_AUDIT_ACTIONS = (
    "admin_delete_pin",
    "admin_delete_comment",
    "role_assign",
    "role_revoke",
    "kyc_submit",
    "kyc_approve",
    "kyc_reject",
    "kyc_need_more_info",
)

OLD_AUDIT_ACTIONS = (
    "admin_delete_pin",
    "admin_delete_comment",
    "role_assign",
    "role_revoke",
)


def upgrade() -> None:
    op.drop_constraint("ck_audit_logs_action", "audit_logs", type_="check")
    op.create_check_constraint(
        "ck_audit_logs_action",
        "audit_logs",
        "action IN ('{}')".format("', '".join(KYC_AUDIT_ACTIONS)),
    )

    op.create_table(
        "companies",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "owner_user_id",
            sa.Integer(),
            sa.ForeignKey("users.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("display_name", sa.String(length=200), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("industry", sa.String(length=100), nullable=True),
        sa.Column("size_min", sa.Integer(), nullable=True),
        sa.Column("size_max", sa.Integer(), nullable=True),
        sa.Column("website", sa.String(length=255), nullable=True),
        sa.Column("domain", sa.String(length=255), nullable=True),
        sa.Column("registration_country", sa.String(length=10), nullable=False),
        sa.Column(
            "registration_authority",
            sa.String(length=100),
            nullable=False,
            server_default="NATIONAL",
        ),
        sa.Column("registration_type", sa.String(length=50), nullable=False),
        sa.Column("registration_number_raw", sa.String(length=100), nullable=False),
        sa.Column("registration_number_normalized", sa.String(length=100), nullable=False),
        sa.Column("tax_id", sa.String(length=100), nullable=True),
        sa.Column("vat_number", sa.String(length=100), nullable=True),
        sa.Column(
            "status",
            sa.String(length=30),
            nullable=False,
            server_default="pending_verification",
        ),
        sa.Column("verified_at", sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column("deleted_at", sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column("delete_reason", sa.String(length=100), nullable=True),
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
            "status IN ('pending_verification', 'active', 'rejected', 'suspended', 'soft_deleted')",
            name="ck_companies_status",
        ),
        sa.UniqueConstraint(
            "registration_country",
            "registration_authority",
            "registration_type",
            "registration_number_normalized",
            name="uq_companies_legal_entity",
        ),
    )
    op.create_index("ix_companies_status", "companies", ["status"])
    op.create_index(
        "uq_companies_owner_user_id",
        "companies",
        ["owner_user_id"],
        unique=True,
        postgresql_where=sa.text("owner_user_id IS NOT NULL"),
    )

    op.create_table(
        "company_branches",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "company_id",
            sa.Integer(),
            sa.ForeignKey("companies.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("label", sa.String(length=100), nullable=True),
        sa.Column("address_line", sa.String(length=300), nullable=False),
        sa.Column("city", sa.String(length=100), nullable=True),
        sa.Column("country", sa.String(length=10), nullable=True),
        sa.Column("is_primary", sa.Boolean(), nullable=False, server_default=sa.text("false")),
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
    )
    op.create_index("ix_company_branches_company_id", "company_branches", ["company_id"])

    op.create_table(
        "company_verification_requests",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "company_id",
            sa.Integer(),
            sa.ForeignKey("companies.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "requester_user_id",
            sa.Integer(),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("status", sa.String(length=30), nullable=False, server_default="pending"),
        sa.Column("signer_full_name", sa.String(length=200), nullable=False),
        sa.Column("signed_at", sa.TIMESTAMP(timezone=True), nullable=False),
        sa.Column("signer_ip", sa.String(length=64), nullable=True),
        sa.Column("signer_user_agent", sa.String(length=400), nullable=True),
        sa.Column("terms_version", sa.String(length=50), nullable=False),
        sa.Column("company_email", sa.String(length=200), nullable=False),
        sa.Column("company_email_confirmed_at", sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column("admin_note", sa.Text(), nullable=True),
        sa.Column("rejection_reason", sa.Text(), nullable=True),
        sa.Column("primary_document_language", sa.String(length=20), nullable=False),
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
            "status IN ('pending', 'need_more_info', 'approved', 'rejected')",
            name="ck_company_verification_requests_status",
        ),
    )
    op.create_index(
        "ix_cvr_company_status",
        "company_verification_requests",
        ["company_id", "status"],
    )
    op.create_index(
        "ix_cvr_requester_user_id",
        "company_verification_requests",
        ["requester_user_id"],
    )

    op.create_table(
        "company_verification_documents",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "request_id",
            sa.Integer(),
            sa.ForeignKey("company_verification_requests.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("doc_type", sa.String(length=50), nullable=False),
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
        sa.CheckConstraint(
            "doc_type IN ("
            "'business_registration_document', 'tax_registration_document', "
            "'authorization_evidence', 'identity_document', 'document_translation'"
            ")",
            name="ck_company_verification_documents_doc_type",
        ),
    )
    op.create_index(
        "ix_cvd_request_doc_type",
        "company_verification_documents",
        ["request_id", "doc_type"],
    )


def downgrade() -> None:
    op.drop_index("ix_cvd_request_doc_type", table_name="company_verification_documents")
    op.drop_table("company_verification_documents")
    op.drop_index("ix_cvr_requester_user_id", table_name="company_verification_requests")
    op.drop_index("ix_cvr_company_status", table_name="company_verification_requests")
    op.drop_table("company_verification_requests")
    op.drop_index("ix_company_branches_company_id", table_name="company_branches")
    op.drop_table("company_branches")
    op.drop_index("uq_companies_owner_user_id", table_name="companies")
    op.drop_index("ix_companies_status", table_name="companies")
    op.drop_table("companies")

    op.drop_constraint("ck_audit_logs_action", "audit_logs", type_="check")
    op.create_check_constraint(
        "ck_audit_logs_action",
        "audit_logs",
        "action IN ('{}')".format("', '".join(OLD_AUDIT_ACTIONS)),
    )
