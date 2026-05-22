"""add embedding to document chunks

Revision ID: 5a8f9ecb1fd2
Revises: e926689bbff1
Create Date: 2026-05-21 10:08:21.389279

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from pgvector.sqlalchemy import Vector


# revision identifiers, used by Alembic.
revision: str = '5a8f9ecb1fd2'
down_revision: Union[str, Sequence[str], None] = 'e926689bbff1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")
    op.add_column(
        "document_chunks",
        sa.Column("embedding", Vector(384), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("document_chunks", "embedding")
