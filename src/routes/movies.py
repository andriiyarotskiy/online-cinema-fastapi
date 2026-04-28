from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import and_, delete, select

from database import (
    AsyncSessionDep,
    CertificationModel,
    FavoriteMovieModel,
    MovieCommentLikeModel,
    MovieCommentModel,
    MovieCommentNotificationModel,
    MovieCommentNotificationTypeEnum,
    MovieModel,
    MovieRatingModel,
    MovieVoteModel,
    UserModel,
)
from database.utils import commit_or_500
from schemas.accounts import MessageResponseSchema
from schemas.movies import (
    MovieCommentCreateRequestSchema,
    MovieCommentNotificationResponseSchema,
    MovieCommentResponseSchema,
    MovieCreateSchema,
    MovieDetailResponseSchema,
    MovieListResponseSchema,
    MovieRatingRequestSchema,
    MovieUpdateSchema,
    MovieVoteRequestSchema,
)
from security.auth import CurrentUserDep, get_current_user
from security.permissions import ModeratorDep
from services.movies import (
    _get_movie_or_404,
    _resolve_related_entities,
    CatalogQueryParams,
    get_catalog_query_params,
    _apply_catalog_sort,
    _apply_catalog_filters,
    _movie_base_stmt,
    _paginate_movies,
)

router = APIRouter()


@router.post(
    "/movies/",
    response_model=MovieDetailResponseSchema,
    status_code=status.HTTP_201_CREATED,
)
async def create_movie(
    movie_data: MovieCreateSchema,
    db: AsyncSessionDep,
    _: ModeratorDep,
) -> MovieDetailResponseSchema:
    exists = await db.scalar(
        select(MovieModel).where(
            and_(
                MovieModel.name == movie_data.name,
                MovieModel.year == movie_data.year,
                MovieModel.time == movie_data.time,
            )
        )
    )
    if exists:
        raise HTTPException(status_code=409, detail="Movie already exists.")
    cert = await db.scalar(
        select(CertificationModel).where(
            CertificationModel.id == movie_data.certification_id
        )
    )
    if not cert:
        raise HTTPException(status_code=404, detail="Certification not found.")
    genres, stars, directors = await _resolve_related_entities(
        db, movie_data.genre_ids, movie_data.star_ids, movie_data.director_ids
    )
    new_movie = MovieModel(
        **movie_data.model_dump(exclude={"genre_ids", "star_ids", "director_ids"})
    )
    new_movie.genres = genres
    new_movie.stars = stars
    new_movie.directors = directors
    db.add(new_movie)
    await commit_or_500(db, new_movie, attribute_names=["genres", "stars", "directors"])

    return MovieDetailResponseSchema.model_validate(new_movie)


@router.get(
    "/movies/", response_model=MovieListResponseSchema, status_code=status.HTTP_200_OK
)
async def get_movies(
    db: AsyncSessionDep,
    params: CatalogQueryParams = Depends(get_catalog_query_params),
) -> MovieListResponseSchema:
    stmt = _apply_catalog_sort(
        _apply_catalog_filters(_movie_base_stmt(), params), params
    )
    return await _paginate_movies(db, stmt, params)


@router.get(
    "/movies/{movie_id}/",
    response_model=MovieDetailResponseSchema,
    status_code=status.HTTP_200_OK,
)
async def get_movie_detail(
    movie_id: int, db: AsyncSessionDep
) -> MovieDetailResponseSchema:
    movie = await _get_movie_or_404(db, movie_id)
    return MovieDetailResponseSchema.model_validate(movie)


@router.put(
    "/movies/{movie_id}/",
    response_model=MovieDetailResponseSchema,
    status_code=status.HTTP_200_OK,
)
async def update_movie(
    movie_id: int,
    movie_data: MovieUpdateSchema,
    db: AsyncSessionDep,
    _: ModeratorDep,
) -> MovieDetailResponseSchema:
    movie = await _get_movie_or_404(db, movie_id)

    payload = movie_data.model_dump(exclude_unset=True)
    if "certification_id" in payload:
        cert = await db.scalar(
            select(CertificationModel).where(
                CertificationModel.id == payload["certification_id"]
            )
        )
        if not cert:
            raise HTTPException(status_code=404, detail="Certification not found.")

    movie_name = movie_data.name or movie.name
    movie_year = movie_data.year or movie.year
    movie_time = movie_data.time or movie.time

    exists = await db.scalar(
        select(MovieModel).where(
            and_(
                MovieModel.name == movie_name,
                MovieModel.year == movie_year,
                MovieModel.time == movie_time,
            )
        )
    )

    if exists:
        raise HTTPException(
            status_code=409, detail="Movie with this name|year|time already exists."
        )

    genre_ids = payload.pop("genre_ids", None)
    star_ids = payload.pop("star_ids", None)
    director_ids = payload.pop("director_ids", None)

    for key, value in payload.items():
        setattr(movie, key, value)

    if genre_ids is not None or star_ids is not None or director_ids is not None:
        genres, stars, directors = await _resolve_related_entities(
            db,
            genre_ids or [genre.id for genre in movie.genres],
            star_ids or [star.id for star in movie.stars],
            director_ids or [director.id for director in movie.directors],
        )
        movie.genres = genres
        movie.stars = stars
        movie.directors = directors

    await commit_or_500(db, movie)
    return MovieDetailResponseSchema.model_validate(movie)


@router.delete("/movies/{movie_id}/", response_model=MessageResponseSchema)
async def delete_movie(
    movie_id: int,
    db: AsyncSessionDep,
    _: ModeratorDep,
) -> MessageResponseSchema:
    movie = await db.scalar(select(MovieModel).where(MovieModel.id == movie_id))
    if not movie:
        raise HTTPException(status_code=404, detail="Movie not found.")
    await db.delete(movie)
    await commit_or_500(db)
    return MessageResponseSchema(message="Movie deleted successfully.")


@router.post("/movies/{movie_id}/vote/", response_model=MessageResponseSchema)
async def vote_movie(
    movie_id: int,
    vote_data: MovieVoteRequestSchema,
    db: AsyncSessionDep,
    user: CurrentUserDep,
) -> MessageResponseSchema:
    await _get_movie_or_404(db, movie_id)
    vote = await db.scalar(
        select(MovieVoteModel).where(
            MovieVoteModel.movie_id == movie_id, MovieVoteModel.user_id == user.id
        )
    )
    if not vote:
        vote = MovieVoteModel(
            movie_id=movie_id, user_id=user.id, is_liked=vote_data.is_liked
        )
        db.add(vote)
    else:
        vote.is_liked = vote_data.is_liked
    await commit_or_500(db)
    return MessageResponseSchema(message="Movie vote saved successfully.")


@router.post("/movies/{movie_id}/rate/", response_model=MessageResponseSchema)
async def rate_movie(
    movie_id: int,
    rating_data: MovieRatingRequestSchema,
    db: AsyncSessionDep,
    user: CurrentUserDep,
) -> MessageResponseSchema:
    await _get_movie_or_404(db, movie_id)
    rating = await db.scalar(
        select(MovieRatingModel).where(
            MovieRatingModel.movie_id == movie_id, MovieRatingModel.user_id == user.id
        )
    )
    if not rating:
        rating = MovieRatingModel(
            movie_id=movie_id, user_id=user.id, rating=rating_data.rating
        )
        db.add(rating)
    else:
        rating.rating = rating_data.rating
    await commit_or_500(db)
    return MessageResponseSchema(message="Movie rating saved successfully.")


@router.post("/favorites/movies/{movie_id}/", response_model=MessageResponseSchema)
async def add_movie_to_favorites(
    movie_id: int,
    db: AsyncSessionDep,
    user: CurrentUserDep,
) -> MessageResponseSchema:
    await _get_movie_or_404(db, movie_id)
    favorite = await db.scalar(
        select(FavoriteMovieModel).where(
            FavoriteMovieModel.movie_id == movie_id,
            FavoriteMovieModel.user_id == user.id,
        )
    )
    if favorite:
        return MessageResponseSchema(message="Movie already in favorites.")
    db.add(FavoriteMovieModel(movie_id=movie_id, user_id=user.id))
    await commit_or_500(db)
    return MessageResponseSchema(message="Movie added to favorites.")


@router.delete("/favorites/movies/{movie_id}/", response_model=MessageResponseSchema)
async def remove_movie_from_favorites(
    movie_id: int,
    db: AsyncSessionDep,
    user: CurrentUserDep,
) -> MessageResponseSchema:
    result = await db.execute(
        delete(FavoriteMovieModel).where(
            FavoriteMovieModel.movie_id == movie_id,
            FavoriteMovieModel.user_id == user.id,
        )
    )
    await commit_or_500(db)
    if not result.rowcount:
        raise HTTPException(status_code=404, detail="Movie is not in favorites.")
    return MessageResponseSchema(message="Movie removed from favorites.")


@router.get(
    "/favorites/movies/",
    response_model=MovieListResponseSchema,
    status_code=status.HTTP_200_OK,
)
async def get_favorite_movies(
    db: AsyncSessionDep,
    params: CatalogQueryParams = Depends(get_catalog_query_params),
    user: UserModel = Depends(get_current_user),
) -> MovieListResponseSchema:
    stmt = _movie_base_stmt().join(
        FavoriteMovieModel,
        and_(
            FavoriteMovieModel.movie_id == MovieModel.id,
            FavoriteMovieModel.user_id == user.id,
        ),
    )
    stmt = _apply_catalog_sort(_apply_catalog_filters(stmt, params), params)
    return await _paginate_movies(db, stmt, params)


@router.post(
    "/movies/{movie_id}/comments/",
    response_model=MovieCommentResponseSchema,
    status_code=status.HTTP_201_CREATED,
)
async def create_comment(
    movie_id: int,
    payload: MovieCommentCreateRequestSchema,
    db: AsyncSessionDep,
    user: CurrentUserDep,
) -> MovieCommentResponseSchema:
    await _get_movie_or_404(db, movie_id)
    parent_comment = None
    if payload.parent_comment_id is not None:
        parent_comment = await db.scalar(
            select(MovieCommentModel).where(
                MovieCommentModel.id == payload.parent_comment_id,
                MovieCommentModel.movie_id == movie_id,
            )
        )
        if not parent_comment:
            raise HTTPException(status_code=404, detail="Parent comment not found.")
    comment = MovieCommentModel(
        movie_id=movie_id,
        user_id=user.id,
        content=payload.content,
        parent_comment_id=payload.parent_comment_id,
    )
    db.add(comment)
    await db.flush()
    if parent_comment and parent_comment.user_id != user.id:
        db.add(
            MovieCommentNotificationModel(
                recipient_user_id=parent_comment.user_id,
                sender_user_id=user.id,
                comment_id=comment.id,
                event_type=MovieCommentNotificationTypeEnum.REPLY,
            )
        )
    await commit_or_500(db, comment)
    return MovieCommentResponseSchema.model_validate(comment)


@router.get(
    "/movies/{movie_id}/comments/",
    response_model=list[MovieCommentResponseSchema],
    status_code=status.HTTP_200_OK,
)
async def get_movie_comments(
    movie_id: int, db: AsyncSessionDep
) -> list[MovieCommentResponseSchema]:
    await _get_movie_or_404(db, movie_id)
    comments = list(
        (
            await db.execute(
                select(MovieCommentModel)
                .where(MovieCommentModel.movie_id == movie_id)
                .order_by(MovieCommentModel.created_at.desc())
            )
        ).scalars()
    )
    return [MovieCommentResponseSchema.model_validate(comment) for comment in comments]


@router.post(
    "/movies/{movie_id}/comments/{comment_id}/like/",
    response_model=MessageResponseSchema,
)
async def like_comment(
    movie_id: int,
    comment_id: int,
    db: AsyncSessionDep,
    user: CurrentUserDep,
) -> MessageResponseSchema:
    comment = await db.scalar(
        select(MovieCommentModel).where(
            MovieCommentModel.id == comment_id, MovieCommentModel.movie_id == movie_id
        )
    )
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found.")
    like = await db.scalar(
        select(MovieCommentLikeModel).where(
            MovieCommentLikeModel.comment_id == comment_id,
            MovieCommentLikeModel.user_id == user.id,
        )
    )
    if like:
        return MessageResponseSchema(message="Comment already liked.")
    db.add(MovieCommentLikeModel(comment_id=comment_id, user_id=user.id))
    if comment.user_id != user.id:
        db.add(
            MovieCommentNotificationModel(
                recipient_user_id=comment.user_id,
                sender_user_id=user.id,
                comment_id=comment_id,
                comment_like_user_id=user.id,
                comment_like_comment_id=comment_id,
                event_type=MovieCommentNotificationTypeEnum.LIKE,
            )
        )
    await commit_or_500(db)
    return MessageResponseSchema(message="Comment liked successfully.")


@router.get(
    "/movies/comments/notifications/",
    response_model=list[MovieCommentNotificationResponseSchema],
    status_code=status.HTTP_200_OK,
)
async def get_comment_notifications(
    db: AsyncSessionDep,
    user: CurrentUserDep,
) -> list[MovieCommentNotificationResponseSchema]:
    notifications = list(
        (
            await db.execute(
                select(MovieCommentNotificationModel)
                .where(MovieCommentNotificationModel.recipient_user_id == user.id)
                .order_by(MovieCommentNotificationModel.created_at.desc())
            )
        ).scalars()
    )
    return [
        MovieCommentNotificationResponseSchema.model_validate(notification)
        for notification in notifications
    ]
