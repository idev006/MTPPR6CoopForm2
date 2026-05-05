"""002 loan tables -- applications, drafts, generated_pdfs, attachments, audit_logs

Revision ID: 002
Revises: 001
Create Date: 2026-04-26
"""
from alembic import op
import sqlalchemy as sa

revision = "002"
down_revision = "001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "loan_applications",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("application_no", sa.String(30), nullable=False),
        sa.Column("applicant_id", sa.Uuid(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("form_type", sa.String(20), nullable=False),
        sa.Column("form_version", sa.String(10), nullable=False, server_default="1.0"),
        sa.Column("status", sa.String(20), nullable=False, server_default="draft"),
        sa.Column("requested_amount", sa.Numeric(12, 2), nullable=True),
        sa.Column("requested_installments", sa.Integer(), nullable=True),
        sa.Column("loan_purpose", sa.Text(), nullable=True),
        sa.Column("form_data", sa.JSON(), nullable=False, server_default="{}"),
        sa.Column("guarantors", sa.JSON(), nullable=False, server_default="[]"),
        sa.Column("reviewed_by", sa.Uuid(), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("review_remarks", sa.Text(), nullable=True),
        sa.Column("submitted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("reviewed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP")),
    )
    op.create_index("idx_apps_application_no", "loan_applications", ["application_no"], unique=True)
    op.create_index("idx_apps_applicant_id",   "loan_applications", ["applicant_id"])
    op.create_index("idx_apps_status",         "loan_applications", ["status"])
    op.create_index("idx_apps_form_type",      "loan_applications", ["form_type"])
    op.create_index("idx_apps_submitted_at",   "loan_applications", ["submitted_at"])

    op.create_table(
        "draft_sessions",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("user_id", sa.Uuid(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("form_type", sa.String(20), nullable=False),
        sa.Column("form_data", sa.JSON(), nullable=False, server_default="{}"),
        sa.Column("current_step", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("last_saved_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("idx_draft_user_form_type", "draft_sessions", ["user_id", "form_type"], unique=True)
    op.create_index("idx_drafts_expires_at",    "draft_sessions", ["expires_at"])

    op.create_table(
        "generated_pdfs",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("application_id", sa.Uuid(), sa.ForeignKey("loan_applications.id", ondelete="CASCADE"), nullable=False),
        sa.Column("storage_path", sa.String(500), nullable=False),
        sa.Column("file_name", sa.String(255), nullable=False),
        sa.Column("file_size_bytes", sa.BigInteger(), nullable=True),
        sa.Column("checksum_sha256", sa.String(64), nullable=True),
        sa.Column("generated_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP")),
    )
    op.create_index("idx_pdfs_application_id", "generated_pdfs", ["application_id"], unique=True)

    op.create_table(
        "attachments",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("application_id", sa.Uuid(), sa.ForeignKey("loan_applications.id", ondelete="CASCADE"), nullable=False),
        sa.Column("file_type", sa.String(50), nullable=False),
        sa.Column("storage_path", sa.String(500), nullable=False),
        sa.Column("original_filename", sa.String(255), nullable=False),
        sa.Column("file_size_bytes", sa.BigInteger(), nullable=True),
        sa.Column("mime_type", sa.String(100), nullable=True),
        sa.Column("uploaded_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP")),
    )

    op.create_table(
        "audit_logs",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("user_id", sa.Uuid(), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("action", sa.String(20), nullable=False),
        sa.Column("entity_type", sa.String(50), nullable=True),
        sa.Column("entity_id", sa.Uuid(), nullable=True),
        sa.Column("old_values", sa.JSON(), nullable=True),
        sa.Column("new_values", sa.JSON(), nullable=True),
        sa.Column("ip_address", sa.String(45), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP")),
    )
    op.create_index("idx_audit_user_id",   "audit_logs", ["user_id"])
    op.create_index("idx_audit_entity",    "audit_logs", ["entity_type", "entity_id"])
    op.create_index("idx_audit_created_at","audit_logs", ["created_at"])


def downgrade() -> None:
    op.drop_table("audit_logs")
    op.drop_table("attachments")
    op.drop_table("generated_pdfs")
    op.drop_table("draft_sessions")
    op.drop_table("loan_applications")
