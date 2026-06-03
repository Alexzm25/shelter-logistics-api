"""add worker_request and worker_request_item tables

Revision ID: 0004
Revises: 0003
Create Date: 2026-06-02

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "0004"
down_revision: Union[str, Sequence[str], None] = "0003"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "worker_request",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("camp_id", sa.Integer(), nullable=False),
        sa.Column("worker_person_id", sa.Integer(), nullable=False),
        sa.Column("request_status_id", sa.Integer(), server_default=sa.text("0"), nullable=False),
        sa.ForeignKeyConstraint(["camp_id"], ["camp.id"], ),
        sa.ForeignKeyConstraint(["worker_person_id"], ["person.id"], ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "worker_request_item",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("worker_request_id", sa.Integer(), nullable=False),
        sa.Column("inventory_resource_id", sa.Integer(), nullable=False),
        sa.Column("quantity", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["worker_request_id"], ["worker_request.id"], ),
        sa.ForeignKeyConstraint(["inventory_resource_id"], ["inventory_resource.id"], ),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("worker_request_item")
    op.drop_table("worker_request")
