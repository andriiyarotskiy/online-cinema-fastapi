from fastapi import APIRouter, status, Depends, HTTPException
from sqlalchemy import select, delete, func, distinct

from database import AsyncSessionDep, UserModel, GenreModel, MovieModel
from database.utils import commit_or_500

from schemas import GenreResponseSchema, GenreRequestSchema, PositiveIntList
from schemas.movies import GenreWithCountResponseSchema
from security.permissions import get_moderator_user

router = APIRouter()


@router.post(
    "/",
    response_model=GenreResponseSchema,
    status_code=status.HTTP_201_CREATED,
)
async def create_genre(
    genre: GenreRequestSchema,
    db: AsyncSessionDep,
    _: UserModel = Depends(get_moderator_user),
) -> GenreResponseSchema:
    stmt_profile = select(GenreModel).where(GenreModel.name == genre.name)
    existing_genre = await db.scalar(stmt_profile)
    if existing_genre:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Genre with this name already exists",
        )

    new_genre = GenreModel(**genre.model_dump())

    db.add(new_genre)
    await commit_or_500(db, new_genre)
    return GenreResponseSchema.model_validate(new_genre)


@router.get(
    "/",
    response_model=list[GenreResponseSchema],
    status_code=status.HTTP_200_OK,
)
async def get_genres(db: AsyncSessionDep) -> list[GenreModel]:
    stmt = select(GenreModel).order_by(GenreModel.id.desc())
    result = await db.execute(stmt)
    genres = result.scalars().all()
    return list(genres)


@router.put(
    "/{genre_id}/", response_model=GenreResponseSchema, status_code=status.HTTP_200_OK
)
async def update_genre(
    genre_id: int,
    genre_data: GenreRequestSchema,
    db: AsyncSessionDep,
    _: UserModel = Depends(get_moderator_user),
) -> GenreResponseSchema:
    genre = await db.scalar(select(GenreModel).where(GenreModel.id == genre_id))
    if not genre:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Genre not found."
        )
    genre_data = genre_data.model_dump()
    for key, value in genre_data.items():
        setattr(genre, key, value)

    await commit_or_500(db, genre)
    return GenreResponseSchema.model_validate(genre)


@router.delete("/")
async def delete_genres(
    ids: PositiveIntList,
    db: AsyncSessionDep,
    _: UserModel = Depends(get_moderator_user),
):
    result = await db.execute(delete(GenreModel).where(GenreModel.id.in_(ids)))
    await commit_or_500(db)
    return {"message": f"{result.rowcount} genres were successfully deleted"}


@router.get(
    "/stats/",
    response_model=list[GenreWithCountResponseSchema],
    status_code=status.HTTP_200_OK,
)
async def genres_with_movie_counts(
    db: AsyncSessionDep,
) -> list[GenreWithCountResponseSchema]:
    stmt = (
        select(
            GenreModel.id,
            GenreModel.name,
            func.count(distinct(MovieModel.id)).label("movies_count"),
        )
        .outerjoin(GenreModel.movies)
        .group_by(GenreModel.id, GenreModel.name)
        .order_by(GenreModel.name.asc())
    )
    rows = (await db.execute(stmt)).all()
    return [
        GenreWithCountResponseSchema(
            id=row.id, name=row.name, movies_count=row.movies_count
        )
        for row in rows
    ]
