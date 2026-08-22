"""remove email unique constraint

Revision ID: 96b3bc52bded
Revises: 10515b76b444
Create Date: 2026-08-22 19:06:08.352062

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '96b3bc52bded'
down_revision: Union[str, None] = '10515b76b444'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_constraint('users_email_key', 'users', type_='unique')


def downgrade() -> None:
    op.create_unique_constraint('users_email_key', 'users', ['email'])
