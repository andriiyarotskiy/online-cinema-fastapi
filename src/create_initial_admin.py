import argparse
import asyncio
from getpass import getpass
import socket

from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError

from database.models.accounts import UserGroupEnum, UserGroupModel, UserModel
from database.session_postgresql import AsyncPostgresqlSessionLocal


async def create_initial_admin(email: str) -> None:
    normalized_email = email.strip().lower()
    if not normalized_email:
        raise ValueError("Email is required.")

    password = getpass("Admin password: ")
    password_confirm = getpass("Confirm admin password: ")
    if not password:
        raise ValueError("Password cannot be empty.")
    if password != password_confirm:
        raise ValueError("Passwords do not match.")

    async with AsyncPostgresqlSessionLocal() as session:
        admin_group = await session.scalar(
            select(UserGroupModel).where(UserGroupModel.name == UserGroupEnum.ADMIN)
        )
        if not admin_group:
            raise RuntimeError(
                "Admin group is missing. Start app once to bootstrap user groups."
            )

        existing_admin = await session.scalar(
            select(UserModel).where(UserModel.group_id == admin_group.id)
        )
        if existing_admin:
            raise RuntimeError(
                "Admin already exists. Use admin role-change endpoint instead."
            )

        existing_user = await session.scalar(
            select(UserModel).where(UserModel.email == normalized_email)
        )
        if existing_user:
            existing_user.group_id = admin_group.id
            existing_user.is_active = True
            existing_user.password = password
        else:
            admin = UserModel.create(
                email=normalized_email,
                raw_password=password,
                group_id=admin_group.id,
            )
            admin.is_active = True
            session.add(admin)

        await session.commit()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Create first admin user.")
    parser.add_argument("--email", required=True, help="Admin email")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    try:
        asyncio.run(create_initial_admin(email=args.email))
    except (SQLAlchemyError, socket.gaierror) as error:
        raise RuntimeError(
            "Database connection failed. Check POSTGRES_HOST/POSTGRES_DB_PORT/"
            "POSTGRES_USER/POSTGRES_PASSWORD in your .env file and make sure "
            "the database container/service is running."
        ) from error
    print("Initial admin user is ready.")


if __name__ == "__main__":
    main()
