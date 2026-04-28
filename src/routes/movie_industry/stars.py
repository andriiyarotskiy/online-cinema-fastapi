from fastapi import APIRouter, status, HTTPException
from sqlalchemy import select, delete

from database import AsyncSessionDep, StarModel
from database.utils import commit_or_500
from schemas.movies import StarResponseSchema, StarRequestSchema, PositiveIntList
from security.permissions import ModeratorDep

router = APIRouter()


@router.post(
    "/", response_model=StarResponseSchema, status_code=status.HTTP_201_CREATED
)
async def create_star(
    star: StarRequestSchema,
    db: AsyncSessionDep,
    _: ModeratorDep,
) -> StarResponseSchema:
    exists = await db.scalar(select(StarModel).where(StarModel.name == star.name))
    if exists:
        raise HTTPException(
            status_code=400, detail="Star with this name already exists."
        )
    new_star = StarModel(**star.model_dump())
    db.add(new_star)
    await commit_or_500(db, new_star)
    return StarResponseSchema.model_validate(new_star)


@router.get(
    "/", response_model=list[StarResponseSchema], status_code=status.HTTP_200_OK
)
async def get_stars(db: AsyncSessionDep) -> list[StarResponseSchema]:
    stars = list(
        (await db.execute(select(StarModel).order_by(StarModel.name.asc()))).scalars()
    )
    return [StarResponseSchema.model_validate(star) for star in stars]


@router.put(
    "/{star_id}/",
    response_model=StarResponseSchema,
    status_code=status.HTTP_200_OK,
)
async def update_star(
    star_id: int,
    star_data: StarRequestSchema,
    db: AsyncSessionDep,
    _: ModeratorDep,
) -> StarResponseSchema:
    star = await db.scalar(select(StarModel).where(StarModel.id == star_id))
    if not star:
        raise HTTPException(status_code=404, detail="Star not found.")
    star.name = star_data.name
    await commit_or_500(db, star)
    return StarResponseSchema.model_validate(star)


@router.delete("/")
async def delete_stars(
    ids: PositiveIntList,
    db: AsyncSessionDep,
    _: ModeratorDep,
):
    result = await db.execute(delete(StarModel).where(StarModel.id.in_(ids)))
    await commit_or_500(db)
    return {"message": f"{result.rowcount} stars were successfully deleted"}
