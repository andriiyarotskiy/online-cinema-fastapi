from dataclasses import dataclass

from typing import Literal, Sequence

from fastapi import Query, HTTPException, status
from sqlalchemy import select, or_, func, case, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload, with_expression

from database import MovieModel, GenreModel, StarModel, DirectorModel, MovieVoteModel
from schemas.movies import MovieListResponseSchema, MovieListItemResponseSchema

per_page_default = 20


@dataclass
class CatalogQueryParams:
    page: int = 1
    per_page: int = per_page_default
    year_from: int | None = None
    year_to: int | None = None
    imdb_from: float | None = None
    imdb_to: float | None = None
    genre_id: int | None = None
    certification_id: int | None = None
    search: str | None = None
    sort_by: str = "name"
    sort_order: str = "asc"

    @property
    def offset(self) -> int:
        return (self.page - 1) * self.per_page


def get_catalog_query_params(
    page: int = Query(1, ge=1),
    per_page: int = Query(per_page_default, ge=1, le=100),
    year_from: int | None = Query(None, ge=1888, le=2100),
    year_to: int | None = Query(None, ge=1888, le=2100),
    imdb_from: float | None = Query(None, ge=0, le=10),
    imdb_to: float | None = Query(None, ge=0, le=10),
    genre_id: int | None = Query(None, gt=0),
    certification_id: int | None = Query(None, gt=0),
    search: str | None = Query(None, min_length=1, max_length=255),
    sort_by: Literal["name", "price", "year", "imdb", "votes"] = Query("name"),
    sort_order: Literal["asc", "desc"] = Query("asc"),
) -> CatalogQueryParams:
    if year_from is not None and year_to is not None and year_from > year_to:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="year_from cannot be greater than year_to.",
        )
    if imdb_from is not None and imdb_to is not None and imdb_from > imdb_to:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="imdb_from cannot be greater than imdb_to.",
        )
    return CatalogQueryParams(
        page=page,
        per_page=per_page,
        year_from=year_from,
        year_to=year_to,
        imdb_from=imdb_from,
        imdb_to=imdb_to,
        genre_id=genre_id,
        certification_id=certification_id,
        search=search.strip() if search else None,
        sort_by=sort_by,
        sort_order=sort_order,
    )


likes_expr = func.count(case((MovieVoteModel.is_liked == True, 1)))
dislikes_expr = func.count(case((MovieVoteModel.is_liked == False, 1)))


def _movie_base_stmt():
    return (
        select(MovieModel)
        .outerjoin(MovieModel.user_votes)
        .options(
            selectinload(MovieModel.genres),
            selectinload(MovieModel.stars),
            selectinload(MovieModel.directors),
            with_expression(MovieModel.likes, likes_expr),
            with_expression(MovieModel.dislikes, dislikes_expr),
        )
        .group_by(MovieModel.id)
    )


def _apply_catalog_filters(stmt, params: CatalogQueryParams):
    needs_join = bool(params.search or params.genre_id)
    if needs_join:
        stmt = (
            stmt.outerjoin(MovieModel.stars)
            .outerjoin(MovieModel.directors)
            .outerjoin(MovieModel.genres)
            .distinct()
        )

    if params.year_from is not None:
        stmt = stmt.where(MovieModel.year >= params.year_from)
    if params.year_to is not None:
        stmt = stmt.where(MovieModel.year <= params.year_to)
    if params.imdb_from is not None:
        stmt = stmt.where(MovieModel.imdb >= params.imdb_from)
    if params.imdb_to is not None:
        stmt = stmt.where(MovieModel.imdb <= params.imdb_to)
    if params.genre_id is not None:
        stmt = stmt.where(GenreModel.id == params.genre_id)
    if params.certification_id is not None:
        stmt = stmt.where(MovieModel.certification_id == params.certification_id)
    if params.search:
        pattern = f"%{params.search}%"
        stmt = stmt.where(
            or_(
                MovieModel.name.ilike(pattern),
                MovieModel.description.ilike(pattern),
                StarModel.name.ilike(pattern),
                DirectorModel.name.ilike(pattern),
            )
        )
    return stmt


def _apply_catalog_sort(stmt, params: CatalogQueryParams):
    sort_map = {
        "name": MovieModel.name,
        "price": MovieModel.price,
        "year": MovieModel.year,
        "imdb": MovieModel.imdb,
        "votes": MovieModel.votes,
    }
    sort_col = sort_map[params.sort_by]
    return stmt.order_by(
        sort_col.desc() if params.sort_order == "desc" else sort_col.asc()
    )


async def _paginate_movies(
    db: AsyncSession, stmt, params: CatalogQueryParams
) -> MovieListResponseSchema:
    total_items = await db.scalar(
        select(func.count()).select_from(stmt.order_by(None).subquery())
    )
    result = await db.execute(stmt.limit(params.per_page).offset(params.offset))
    movies = list(result.scalars().unique().all())
    total = int(total_items or 0)
    total_pages = max(1, (total + params.per_page - 1) // params.per_page)
    prev_page = (
        None
        if params.page <= 1
        else f"?page={params.page - 1}&per_page={params.per_page}"
    )
    next_page = (
        None
        if params.page >= total_pages
        else f"?page={params.page + 1}&per_page={params.per_page}"
    )
    return MovieListResponseSchema(
        movies=[MovieListItemResponseSchema.model_validate(movie) for movie in movies],
        prev_page=prev_page,
        next_page=next_page,
        total_pages=total_pages,
        total_items=total,
    )


async def _get_movie_or_404(db: AsyncSession, movie_id: int) -> MovieModel:
    movie = await db.scalar(
        _movie_base_stmt().where(MovieModel.id == movie_id).limit(1)
    )
    if not movie:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Movie not found.",
        )
    return movie


async def _resolve_related_entities(
    db: AsyncSession,
    genre_ids: Sequence[int],
    star_ids: Sequence[int],
    director_ids: Sequence[int],
):
    genres = (
        list(
            (
                await db.execute(select(GenreModel).where(GenreModel.id.in_(genre_ids)))
            ).scalars()
        )
        if genre_ids
        else []
    )
    stars = (
        list(
            (
                await db.execute(select(StarModel).where(StarModel.id.in_(star_ids)))
            ).scalars()
        )
        if star_ids
        else []
    )
    directors = (
        list(
            (
                await db.execute(
                    select(DirectorModel).where(DirectorModel.id.in_(director_ids))
                )
            ).scalars()
        )
        if director_ids
        else []
    )
    if len(genres) != len(set(genre_ids)):
        raise HTTPException(status_code=404, detail="One or more genres not found.")
    if len(stars) != len(set(star_ids)):
        raise HTTPException(status_code=404, detail="One or more stars not found.")
    if len(directors) != len(set(director_ids)):
        raise HTTPException(status_code=404, detail="One or more directors not found.")
    return genres, stars, directors


async def check_movie_uniqueness(movie, payload, db) -> bool:
    if any(field in payload for field in ("name", "year", "time")):
        new_name = payload.get("name", movie.name)
        new_year = payload.get("year", movie.year)
        new_time = payload.get("time", movie.time)

        conflict = await db.scalar(
            select(MovieModel.id).where(
                and_(
                    MovieModel.name == new_name,
                    MovieModel.year == new_year,
                    MovieModel.time == new_time,
                    MovieModel.id != movie.id,
                )
            )
        )
        return conflict
    return False
