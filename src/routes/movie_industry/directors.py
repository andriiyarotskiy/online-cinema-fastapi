from fastapi import APIRouter, HTTPException, status
from sqlalchemy import select, delete

from database import AsyncSessionDep, DirectorModel
from database.utils import commit_or_500
from schemas.movies import (
    DirectorResponseSchema,
    DirectorRequestSchema,
    PositiveIntList,
)
from security.permissions import ModeratorDep

router = APIRouter()


@router.post(
    "/",
    response_model=DirectorResponseSchema,
    status_code=status.HTTP_201_CREATED,
)
async def create_director(
    director: DirectorRequestSchema,
    db: AsyncSessionDep,
    # _: ModeratorDep,
) -> DirectorResponseSchema:
    exists = await db.scalar(
        select(DirectorModel).where(DirectorModel.name == director.name)
    )
    if exists:
        raise HTTPException(
            status_code=400, detail="Director with this name already exists."
        )
    new_director = DirectorModel(**director.model_dump())
    db.add(new_director)
    await commit_or_500(db, new_director)
    return DirectorResponseSchema.model_validate(new_director)


@router.get(
    "/",
    response_model=list[DirectorResponseSchema],
    status_code=status.HTTP_200_OK,
)
async def get_directors(db: AsyncSessionDep) -> list[DirectorResponseSchema]:
    directors = list(
        (
            await db.execute(select(DirectorModel).order_by(DirectorModel.name.asc()))
        ).scalars()
    )
    return [DirectorResponseSchema.model_validate(director) for director in directors]


@router.put(
    "/{director_id}/",
    response_model=DirectorResponseSchema,
    status_code=status.HTTP_200_OK,
)
async def update_director(
    director_id: int,
    director_data: DirectorRequestSchema,
    db: AsyncSessionDep,
    _: ModeratorDep,
) -> DirectorResponseSchema:
    director = await db.scalar(
        select(DirectorModel).where(DirectorModel.id == director_id)
    )
    if not director:
        raise HTTPException(status_code=404, detail="Director not found.")
    director.name = director_data.name
    await commit_or_500(db, director)
    return DirectorResponseSchema.model_validate(director)


@router.delete("/")
async def delete_directors(
    ids: PositiveIntList,
    db: AsyncSessionDep,
    _: ModeratorDep,
):
    result = await db.execute(delete(DirectorModel).where(DirectorModel.id.in_(ids)))
    await commit_or_500(db)
    return {"message": f"{result.rowcount} directors were successfully deleted"}
