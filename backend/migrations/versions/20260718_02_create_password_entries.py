"""create password entries table

Revision ID: 20260718_02
Revises: 20260717_01
Create Date: 2026-07-18
"""
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20260718_02"
down_revision: str | None = "20260717_01"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "password_entries",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("owner_id", sa.Integer(), nullable=False),
        sa.Column("service_name", sa.String(length=200), nullable=False),
        sa.Column("username", sa.String(length=255), nullable=False),
        sa.Column("encrypted_password", sa.Text(), nullable=False),
        sa.Column("website", sa.String(length=2048), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["owner_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_password_entries_owner_id", "password_entries", ["owner_id"], unique=False
    )
    op.create_index(
        "ix_password_entries_owner_service",
        "password_entries",
        ["owner_id", "service_name"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_password_entries_owner_service", table_name="password_entries")
    op.drop_index("ix_password_entries_owner_id", table_name="password_entries")
    op.drop_table("password_entries")

