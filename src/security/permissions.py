from typing import Annotated

from fastapi import Depends, HTTPException, status

from database import UserModel, UserGroupEnum
from security.auth import get_current_user


async def get_moderator_user(user: UserModel = Depends(get_current_user)) -> UserModel:
    if user.group.name not in (UserGroupEnum.MODERATOR, UserGroupEnum.ADMIN):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission for this action.",
        )
    return user


ModeratorDep = Annotated[UserModel, Depends(get_moderator_user)]
