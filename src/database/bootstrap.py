from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database.models.accounts import UserGroupEnum, UserGroupModel


async def ensure_user_groups(session: AsyncSession) -> None:
    existing_result = await session.execute(select(UserGroupModel.name))
    existing_groups = set(existing_result.scalars().all())

    missing_groups = [
        UserGroupModel(name=group_enum)
        for group_enum in UserGroupEnum
        if group_enum not in existing_groups
    ]
    if missing_groups:
        session.add_all(missing_groups)
        await session.flush()


async def bootstrap_auth_data(session: AsyncSession) -> None:
    await ensure_user_groups(session)
