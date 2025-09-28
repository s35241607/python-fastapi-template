"""modify_category_name_unique_constraint

Revision ID: bf26b7859ae8
Revises: 68d74054af42
Create Date: 2025-09-28 08:19:10.261954

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "bf26b7859ae8"
down_revision: str | Sequence[str] | None = "68d74054af42"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    # Drop the existing unique constraint on name
    op.drop_constraint("categories_name_key", "categories", schema="ticket", type_="unique")
    # Create a partial unique index on name where deleted_at IS NULL
    op.create_index(
        "idx_categories_name_unique",
        "categories",
        ["name"],
        schema="ticket",
        unique=True,
        postgresql_where=sa.text("deleted_at IS NULL"),
    )


def downgrade() -> None:
    """Downgrade schema."""
    # Drop the partial unique index
    op.drop_index("idx_categories_name_unique", table_name="categories", schema="ticket")
    # Recreate the original unique constraint on name
    op.create_unique_constraint("categories_name_key", "categories", ["name"], schema="ticket")
