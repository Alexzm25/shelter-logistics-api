"""add production run audit table

Revision ID: 0005
Revises: 0004
Create Date: 2026-06-03

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "0005"
down_revision: Union[str, Sequence[str], None] = "0004"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "production_run_audit",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("executed_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("camp_id", sa.Integer(), nullable=False),
        sa.Column("resources_produced", sa.JSON(), nullable=False),
        sa.ForeignKeyConstraint(["camp_id"], ["camp.id"], ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_production_run_audit_camp_executed_at",
        "production_run_audit",
        ["camp_id", "executed_at"],
    )


def downgrade() -> None:
    op.drop_index("ix_production_run_audit_camp_executed_at", table_name="production_run_audit")
    op.drop_table("production_run_audit")
