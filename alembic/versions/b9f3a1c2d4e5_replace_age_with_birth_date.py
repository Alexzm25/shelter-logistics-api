"""replace age with birth_date in person

Revision ID: b9f3a1c2d4e5
Revises: 8a6306451f2e
Create Date: 2026-06-05 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'b9f3a1c2d4e5'
down_revision: Union[str, Sequence[str], None] = '0006'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('person', sa.Column('birth_date', sa.Date(), nullable=True))

    op.execute(
        "UPDATE person SET birth_date = (CURRENT_DATE - (age * INTERVAL '1 year'))::date"
    )

    op.alter_column('person', 'birth_date', nullable=False)

    op.drop_column('person', 'age')


def downgrade() -> None:
    op.add_column('person', sa.Column('age', sa.Integer(), nullable=True))

    op.execute(
        "UPDATE person SET age = DATE_PART('year', AGE(CURRENT_DATE, birth_date))::INTEGER"
    )

    op.alter_column('person', 'age', nullable=False)

    op.drop_column('person', 'birth_date')
