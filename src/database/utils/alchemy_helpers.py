from typing import Iterable, Optional

from fastapi import HTTPException, status
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession


async def commit_or_500(
    db: AsyncSession, instance=None, attribute_names: Optional[Iterable[str]] = None
):
    try:
        await db.commit()
        if instance is not None:
            await db.refresh(instance, attribute_names)
        return instance
    except SQLAlchemyError as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error occurred.",
        ) from e
