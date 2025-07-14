"""added role table and rmoeved user type id

Revision ID: 0f6df2ecccc0
Revises: 797404c08d89
Create Date: 2025-07-13 22:19:31.302888

"""

from typing import Sequence, Union

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "0f6df2ecccc0"
down_revision: Union[str, None] = "797404c08d89"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1) Create the new table
    op.create_table(
        "user_roles",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("modified_at", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
    )

    # 2) Migrate policies → user_roles
    op.add_column("policies", sa.Column("targeted_role_id", sa.UUID(), nullable=False))
    op.drop_constraint(
        op.f("fk_policies_targeted_user_type"), "policies", type_="foreignkey"
    )
    op.create_foreign_key(
        None, "policies", "user_roles", ["targeted_role_id"], ["id"], ondelete="CASCADE"
    )
    op.drop_column("policies", "targeted_user_type_id")

    op.add_column("users", sa.Column("role_id", sa.UUID(), nullable=True))
    op.drop_constraint(op.f("users_user_type_id_fkey"), "users", type_="foreignkey")
    op.create_foreign_key(
        None, "users", "user_roles", ["role_id"], ["id"], ondelete="SET NULL"
    )
    op.drop_column("users", "user_type_id")
    op.drop_column("users", "user_role_name")

    op.drop_table("user_types")


def downgrade() -> None:
    # 1) Recreate the old user_types table
    op.create_table(
        "user_types",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("name", sa.VARCHAR(), nullable=False),
        sa.Column("user_level", sa.INTEGER(), nullable=True),
        sa.Column("school", sa.UUID(), nullable=False),
        sa.Column("created_at", postgresql.TIMESTAMP(), nullable=False),
        sa.Column("modified_at", postgresql.TIMESTAMP(), nullable=True),
        sa.ForeignKeyConstraint(
            ["school"],
            ["schools.id"],
            name=op.f("user_types_school_fkey"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("user_types_pkey")),
    )

    # 2) Put back the targeted_user_type_id column & FK on policies
    op.add_column(
        "policies",
        sa.Column("targeted_user_type_id", sa.UUID(), nullable=False),
    )
    # drop new FK to user_roles
    op.drop_constraint(None, "policies", type_="foreignkey")
    # recreate old FK to user_types
    op.create_foreign_key(
        op.f("fk_policies_targeted_user_type"),
        "policies",
        "user_types",
        ["targeted_user_type_id"],
        ["id"],
        ondelete="CASCADE",
    )
    op.drop_column("policies", "targeted_role_id")

    # 3) Put back the user_type columns & FK on users
    op.add_column(
        "users",
        sa.Column("user_type_id", sa.UUID(), nullable=True),
    )
    op.add_column(
        "users",
        sa.Column("user_role_name", sa.VARCHAR(), nullable=False),
    )
    # drop new FK to user_roles
    op.drop_constraint(None, "users", type_="foreignkey")
    # recreate old FK to user_types
    op.create_foreign_key(
        op.f("users_user_type_id_fkey"),
        "users",
        "user_types",
        ["user_type_id"],
        ["id"],
        ondelete="CASCADE",
    )
    op.drop_column("users", "role_id")
    op.drop_table("user_roles")
