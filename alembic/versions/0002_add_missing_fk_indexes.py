"""add missing FK indexes

Revision ID: 0002
Revises: 8a6306451f2e
Create Date: 2026-05-25

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '0002'
down_revision: Union[str, Sequence[str], None] = '8a6306451f2e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_index("IX_inventory_movement_transfer_request", "inventory_movement", ["transfer_request_id"])
    op.create_index("IX_exploration_member_exploration", "exploration_member", ["exploration_id"])
    op.create_index("IX_transfer_participants_request", "transfer_participants", ["request_id"])


def downgrade() -> None:
    op.drop_index("IX_inventory_movement_transfer_request", table_name="inventory_movement")
    op.drop_index("IX_exploration_member_exploration", table_name="exploration_member")
    op.drop_index("IX_transfer_participants_request", table_name="transfer_participants")
