"""add llm call events table

Revision ID: 20241005_add_llm_call_events
Revises: 
Create Date: 2024-10-05 17:00:00.000000
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision = "20241005_add_llm_call_events"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "llm_call_events",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("session_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("sessions.id", ondelete="SET NULL"), nullable=True),
        sa.Column("participant_id", sa.String(length=64), nullable=True),
        sa.Column("participant_role", sa.String(length=32), nullable=True),
        sa.Column("participant_name", sa.String(length=128), nullable=True),
        sa.Column("provider", sa.String(length=32), nullable=True),
        sa.Column("model", sa.String(length=128), nullable=True),
        sa.Column("turn_number", sa.Integer(), nullable=True),
        sa.Column("latency_ms", sa.Integer(), nullable=True),
        sa.Column("prompt_text", sa.Text(), nullable=True),
        sa.Column("request_payload", sa.JSON(), nullable=True),
        sa.Column("response_text", sa.Text(), nullable=True),
        sa.Column("response_payload", sa.JSON(), nullable=True),
        sa.Column("status", sa.String(length=32), nullable=False, server_default=sa.text("'unknown'")),
        sa.Column("status_detail", sa.Text(), nullable=True),
        sa.Column("prompt_tokens", sa.Integer(), nullable=True),
        sa.Column("completion_tokens", sa.Integer(), nullable=True),
        sa.Column("total_tokens", sa.Integer(), nullable=True),
        sa.Column("context_snapshot", sa.JSON(), nullable=True),
    )

    op.create_index(
        "ix_llm_call_events_session_created_at",
        "llm_call_events",
        ["session_id", "created_at"],
    )


def downgrade() -> None:
    op.drop_index("ix_llm_call_events_session_created_at", table_name="llm_call_events")
    op.drop_table("llm_call_events")
