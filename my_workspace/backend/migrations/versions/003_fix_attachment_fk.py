"""003 fix attachment fk -- drop FK on attachments.application_id

During the draft phase attachments are stored with application_id = draft_session_id
(a UUID from draft_sessions, not loan_applications). The FK created in 002 breaks
INSERT on PostgreSQL when uploading files before submitting the loan application.

The Attachment model already has no FK defined -- this migration aligns the database
schema with the model.

SQLite note: batch_alter_table with recreate="always" forces a full table rebuild,
which naturally drops all unnamed FK constraints (SQLite does not name FKs the same
way PostgreSQL does, so drop_constraint by name fails on SQLite).

Revision ID: 003
Revises: 002
Create Date: 2026-05-03
"""
from alembic import op
import sqlalchemy as sa
from alembic.operations import ops

revision = "003"
down_revision = "002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # recreate="always" forces batch_alter_table to rebuild the table from scratch.
    # The rebuilt table is defined only by the columns we specify — no FK on application_id.
    # This works identically on both SQLite and PostgreSQL.
    with op.batch_alter_table("attachments", recreate="always") as batch_op:
        pass  # No column changes needed; the recreate drops the unnamed FK


def downgrade() -> None:
    # Re-add FK — note: this will fail on existing rows that have draft_session UUIDs
    # Only safe to run on a database where all attachments belong to loan_applications
    with op.batch_alter_table("attachments", recreate="always") as batch_op:
        batch_op.create_foreign_key(
            "attachments_application_id_fkey",
            "loan_applications",
            ["application_id"],
            ["id"],
            ondelete="CASCADE",
        )
