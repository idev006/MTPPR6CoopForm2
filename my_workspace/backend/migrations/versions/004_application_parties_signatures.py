"""004 application parties and signatures -- snapshot tables for loan applications

application_parties: stores a legal snapshot of every party involved in a loan
  (BORROWER, GUARANTOR, SPOUSE_BORROWER, etc.) at the moment of submission.

signatures: stores the actual signature data (base64) for each party.

These tables were created via Base.metadata.create_all() in dev but were never
captured as Alembic migrations. This migration closes that gap.

Revision ID: 004
Revises: 003
Create Date: 2026-05-03
"""
from alembic import op
import sqlalchemy as sa

revision = "004"
down_revision = "003"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "application_parties",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column(
            "application_id",
            sa.Uuid(),
            sa.ForeignKey("loan_applications.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "member_id",
            sa.Uuid(),
            sa.ForeignKey("users.id"),
            nullable=True,
        ),
        sa.Column("role", sa.String(50), nullable=False),
        sa.Column("full_name", sa.String(255), nullable=False),
        sa.Column("position", sa.String(100), nullable=True),
        sa.Column("department", sa.String(100), nullable=True),
        sa.Column("national_id", sa.String(20), nullable=True),
        sa.Column("address_snapshot", sa.JSON(), nullable=True),
        sa.Column("sequence", sa.Integer(), nullable=False, server_default="0"),
    )
    op.create_index("idx_parties_application_id", "application_parties", ["application_id"])
    op.create_index("idx_parties_role", "application_parties", ["application_id", "role"])

    op.create_table(
        "signatures",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column(
            "party_id",
            sa.Uuid(),
            sa.ForeignKey("application_parties.id", ondelete="CASCADE"),
            nullable=False,
            unique=True,
        ),
        sa.Column("signature_data", sa.Text(), nullable=False),
        sa.Column("ip_address", sa.String(50), nullable=True),
        sa.Column("user_agent", sa.String(255), nullable=True),
        sa.Column(
            "signed_at",
            sa.DateTime(),
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
    )
    op.create_index("idx_signatures_party_id", "signatures", ["party_id"], unique=True)


def downgrade() -> None:
    op.drop_table("signatures")
    op.drop_table("application_parties")
