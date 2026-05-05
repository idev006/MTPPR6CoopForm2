"""006 cancel fields -- add cancelled_at and cancel_reason to loan_applications

Revision ID: 006
Revises: 005
Create Date: 2026-04-30
"""
from alembic import op
import sqlalchemy as sa

revision = "006"
down_revision = "005"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "loan_applications",
        sa.Column("cancelled_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.add_column(
        "loan_applications",
        sa.Column("cancel_reason", sa.Text(), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("loan_applications", "cancel_reason")
    op.drop_column("loan_applications", "cancelled_at")
