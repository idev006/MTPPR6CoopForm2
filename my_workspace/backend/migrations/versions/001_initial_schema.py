"""001 initial schema -- users and member_profiles

Revision ID: 001
Revises:
Create Date: 2026-04-26
"""
from alembic import op
import sqlalchemy as sa

revision = "001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("email", sa.String(255), nullable=False),
        sa.Column("hashed_password", sa.String(255), nullable=False),
        sa.Column("role", sa.String(20), nullable=False),
        sa.Column("member_code", sa.String(20), nullable=True),
        sa.Column("national_id", sa.String(13), nullable=True),
        sa.Column("first_name", sa.String(100), nullable=False),
        sa.Column("last_name", sa.String(100), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="1"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP")),
    )
    # unique index ใช้ได้ทั้ง SQLite และ PostgreSQL
    op.create_index("idx_users_email",       "users", ["email"],       unique=True)
    op.create_index("idx_users_member_code", "users", ["member_code"], unique=True)
    op.create_index("idx_users_national_id", "users", ["national_id"], unique=True)

    op.create_table(
        "member_profiles",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("user_id", sa.Uuid(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("title", sa.String(50), nullable=True),
        sa.Column("position", sa.String(100), nullable=True),
        sa.Column("department", sa.String(200), nullable=True),
        sa.Column("organization", sa.String(200), nullable=True),
        sa.Column("phone", sa.String(20), nullable=True),
        sa.Column("addr_house_no", sa.String(20), nullable=True),
        sa.Column("addr_moo", sa.String(10), nullable=True),
        sa.Column("addr_road", sa.String(100), nullable=True),
        sa.Column("addr_tambon", sa.String(100), nullable=True),
        sa.Column("addr_amphur", sa.String(100), nullable=True),
        sa.Column("addr_province", sa.String(100), nullable=True),
        sa.Column("salary", sa.Numeric(12, 2), nullable=True),
        sa.Column("shares_amount", sa.Numeric(12, 2), nullable=True),
        sa.Column("existing_debt", sa.Numeric(12, 2), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP")),
    )
    op.create_index("idx_member_profiles_user_id", "member_profiles", ["user_id"], unique=True)


def downgrade() -> None:
    op.drop_table("member_profiles")
    op.drop_table("users")
