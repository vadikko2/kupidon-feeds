"""Remove computed fields from feeds table

Revision ID: remove_feeds_computed_fields
Revises: add_views_table
Create Date: 2025-12-07 12:30:00.000000

"""

from collections.abc import Sequence
from typing import Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "remove_feeds_computed_fields"
down_revision: Union[str, None] = "add_views_table"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Remove computed fields from feeds table
    # These fields are now calculated dynamically from related tables
    op.drop_column("feeds", "has_followed")
    op.drop_column("feeds", "has_liked")
    op.drop_column("feeds", "likes_count")
    op.drop_column("feeds", "views_count")


def downgrade() -> None:
    # Restore computed fields (with default values)
    op.add_column(
        "feeds",
        sa.Column("has_followed", sa.Boolean(), nullable=False, server_default="false"),
    )
    op.add_column(
        "feeds",
        sa.Column("has_liked", sa.Boolean(), nullable=False, server_default="false"),
    )
    op.add_column(
        "feeds",
        sa.Column("likes_count", sa.Integer(), nullable=False, server_default="0"),
    )
    op.add_column(
        "feeds",
        sa.Column("views_count", sa.Integer(), nullable=False, server_default="0"),
    )
