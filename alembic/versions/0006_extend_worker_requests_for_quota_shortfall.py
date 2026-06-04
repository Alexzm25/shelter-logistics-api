"""extend worker requests for quota shortfall

Revision ID: 0006
Revises: 0005
Create Date: 2026-06-03

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "0006"
down_revision: Union[str, Sequence[str], None] = "0005"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "worker_request",
        sa.Column("request_type", sa.String(length=40), server_default="RESOURCE_REQUEST", nullable=False),
    )
    op.add_column("worker_request", sa.Column("reason", sa.Text(), nullable=True))
    op.add_column("worker_request", sa.Column("rejection_reason", sa.Text(), nullable=True))
    op.execute(
        "UPDATE worker_request "
        "SET request_type = 'RESOURCE_REQUEST' "
        "WHERE request_type = 'RESOURCE'"
    )


def downgrade() -> None:
    op.drop_column("worker_request", "rejection_reason")
    op.drop_column("worker_request", "reason")
    op.drop_column("worker_request", "request_type")
