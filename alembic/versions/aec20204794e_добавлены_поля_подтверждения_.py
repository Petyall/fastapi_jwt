"""Добавлены поля подтверждения регистрации USER

Revision ID: aec20204794e
Revises: 162c139b5618
Create Date: 2025-06-05 11:44:11.777186

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'aec20204794e'
down_revision: Union[str, None] = '162c139b5618'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('users', sa.Column('email_confirmed', sa.Boolean(), server_default='false', nullable=False))
    op.add_column('users', sa.Column('confirmation_token', sa.Text(), nullable=True))
    op.add_column('users', sa.Column('confirmation_token_created_at', sa.DateTime(), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('users', 'confirmation_token_created_at')
    op.drop_column('users', 'confirmation_token')
    op.drop_column('users', 'email_confirmed')
    # ### end Alembic commands ###
