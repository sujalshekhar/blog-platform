"""Add blog_type to blogs

Revision ID: 6ac43038049c
Revises: ffa62e2adfb2
Create Date: 2026-07-29 22:11:20.997332

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '6ac43038049c'
down_revision: Union[str, Sequence[str], None] = 'ffa62e2adfb2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


from sqlalchemy.dialects import postgresql

def upgrade() -> None:
    """Upgrade schema."""
    blog_type = postgresql.ENUM('ARTICLE', 'TUTORIAL', 'NEWS', 'OPINION', name='blog_type')
    blog_type.create(op.get_bind(), checkfirst=True)
    op.add_column('blogs', sa.Column('blog_type', blog_type, server_default='ARTICLE', nullable=False))


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('blogs', 'blog_type')
    blog_type = postgresql.ENUM('ARTICLE', 'TUTORIAL', 'NEWS', 'OPINION', name='blog_type')
    blog_type.drop(op.get_bind(), checkfirst=True)
