"""Updated certification model

Revision ID: 4da125030bc4
Revises: 1b57869eec8e
Create Date: 2026-04-26 11:51:37.741760

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "4da125030bc4"
down_revision: Union[str, Sequence[str], None] = "1b57869eec8e"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Create ENUM type
    certification_enum = sa.Enum(
        "G", "PG", "A14", "A18", "R", "A", "E", name="certificationenum"
    )
    certification_enum.create(op.get_bind(), checkfirst=True)

    # 2. Convert column type VARCHAR -> ENUM
    op.alter_column(
        "certifications",
        "name",
        type_=certification_enum,
        existing_type=sa.String(length=64),
        existing_nullable=False,
        postgresql_using="name::certificationenum",
    )

    # 3. Insert values
    op.execute("""
               INSERT INTO certifications (name)
               VALUES ('G'),
                      ('PG'),
                      ('A14'),
                      ('A18'),
                      ('R'),
                      ('A'),
                      ('E');
               """)


def downgrade() -> None:
    op.alter_column(
        "certifications",
        "name",
        type_=sa.String(length=64),
        existing_type=sa.Enum(name="certificationenum"),
        existing_nullable=False,
        postgresql_using="name::text",
    )
    op.execute("DROP TYPE IF EXISTS certificationenum;")
