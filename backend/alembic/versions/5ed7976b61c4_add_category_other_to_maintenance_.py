"""add category_other to maintenance requests

Revision ID: 5ed7976b61c4
Revises: 00cbed0b13c5
Create Date: 2026-11-18 15:01:36.744871

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '5ed7976b61c4'
down_revision: Union[str, None] = '00cbed0b13c5'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('maintenance_requests', sa.Column('category_other', sa.String(length=100), nullable=True))
    # Requests already stored as "Other" have no description of the category. Backfill them so the
    # new constraint can be added. Other rows are not changed.
    op.execute(
        "UPDATE maintenance_requests SET category_other = 'Not specified (before category text was required)' "
        "WHERE category = 'Other' AND (category_other IS NULL OR btrim(category_other) = '')"
    )
    # Alembic autogenerate does not emit CHECK constraints, so they are added explicitly.
    op.create_check_constraint(
        'ck_requests_other_category_text',
        'maintenance_requests',
        "category <> 'Other' OR (category_other IS NOT NULL AND length(btrim(category_other)) > 0)",
    )
    op.create_check_constraint(
        'ck_requests_category_other_only_for_other',
        'maintenance_requests',
        "category_other IS NULL OR category = 'Other'",
    )


def downgrade() -> None:
    op.drop_constraint('ck_requests_category_other_only_for_other', 'maintenance_requests', type_='check')
    op.drop_constraint('ck_requests_other_category_text', 'maintenance_requests', type_='check')
    op.drop_column('maintenance_requests', 'category_other')
