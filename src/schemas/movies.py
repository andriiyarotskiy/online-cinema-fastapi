from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Annotated, Optional
from uuid import UUID

from annotated_types import Gt

from pydantic import BaseModel, ConfigDict, Field
from schemas.examples.movies import (
    genre_schema_example,
    star_schema_example,
    director_schema_example,
    movie_create_schema_example,
    movie_detail_schema_example,
    movie_item_schema_example,
    movie_list_response_schema_example,
    movie_update_schema_example,
    movie_vote_schema_example,
    movie_rating_schema_example,
    movie_comment_create_schema_example,
    movie_comment_schema_example,
    movie_notification_schema_example,
    genre_with_count_schema_example,
)

PositiveIntList = list[Annotated[int, Gt(0)]]


class GenreBase(BaseModel):
    name: str = Field(..., min_length=3, max_length=255)


class GenreRequestSchema(GenreBase):
    pass


class GenreResponseSchema(GenreBase):
    model_config = ConfigDict(
        from_attributes=True, json_schema_extra={"examples": [genre_schema_example]}
    )

    id: int


# Star
class StarBase(BaseModel):
    name: str = Field(..., min_length=3, max_length=255)


class StarRequestSchema(StarBase):
    pass


class StarResponseSchema(StarBase):
    model_config = ConfigDict(
        from_attributes=True, json_schema_extra={"examples": [star_schema_example]}
    )

    id: int


# Director
class DirectorBase(BaseModel):
    name: str = Field(..., min_length=8, max_length=255)


class DirectorRequestSchema(DirectorBase):
    pass


class DirectorResponseSchema(DirectorBase):
    model_config = ConfigDict(
        from_attributes=True, json_schema_extra={"examples": [director_schema_example]}
    )

    id: int


# Movie
class MovieBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    year: int = Field(..., ge=1888, le=2100)
    time: int = Field(..., ge=1, le=24 * 60)
    imdb: float = Field(..., ge=0, le=10)
    votes: int = Field(..., ge=0)
    meta_score: Optional[float] = Field(default=None, ge=0, le=100)
    gross: Optional[float] = Field(default=None, ge=0)
    description: str = Field(..., min_length=1)
    price: Decimal = Field(..., ge=Decimal("0.00"))
    certification_id: int = Field(..., gt=0)


class MovieCreateSchema(MovieBase):
    genre_ids: PositiveIntList = Field(default_factory=list)
    star_ids: PositiveIntList = Field(default_factory=list)
    director_ids: PositiveIntList = Field(default_factory=list)

    model_config = ConfigDict(json_schema_extra={"examples": [movie_create_schema_example]})


class MovieUpdateSchema(BaseModel):
    name: Optional[str] = Field(default=None, min_length=1, max_length=255)
    year: Optional[int] = Field(default=None, ge=1888, le=2100)
    time: Optional[int] = Field(default=None, ge=1, le=24 * 60)
    imdb: Optional[float] = Field(default=None, ge=0, le=10)
    votes: Optional[int] = Field(default=None, ge=0)
    meta_score: Optional[float] = Field(default=None, ge=0, le=100)
    gross: Optional[float] = Field(default=None, ge=0)
    description: Optional[str] = Field(default=None, min_length=1)
    price: Optional[Decimal] = Field(default=None, ge=Decimal("0.00"))
    certification_id: Optional[int] = Field(default=None, gt=0)
    genre_ids: Optional[PositiveIntList] = None
    star_ids: Optional[PositiveIntList] = None
    director_ids: Optional[PositiveIntList] = None

    model_config = ConfigDict(json_schema_extra={"examples": [movie_update_schema_example]})


class MovieListItemResponseSchema(BaseModel):
    model_config = ConfigDict(
        from_attributes=True, json_schema_extra={"examples": [movie_item_schema_example]}
    )

    id: int
    uuid: UUID
    name: str
    year: int
    time: int
    imdb: float
    votes: int
    meta_score: Optional[float] = None
    gross: Optional[float] = None
    price: Decimal


class MovieDetailResponseSchema(MovieListItemResponseSchema):
    model_config = ConfigDict(
        from_attributes=True, json_schema_extra={"examples": [movie_detail_schema_example]}
    )

    description: str
    certification_id: int
    genres: list[GenreResponseSchema] = []
    stars: list[StarResponseSchema] = []
    directors: list[DirectorResponseSchema] = []


class MovieListResponseSchema(BaseModel):
    model_config = ConfigDict(json_schema_extra={"examples": [movie_list_response_schema_example]})

    movies: list[MovieListItemResponseSchema]
    prev_page: Optional[str] = None
    next_page: Optional[str] = None
    total_pages: int = Field(..., ge=1)
    total_items: int = Field(..., ge=0)


class MovieVoteRequestSchema(BaseModel):
    is_liked: bool

    model_config = ConfigDict(json_schema_extra={"examples": [movie_vote_schema_example]})


class MovieRatingRequestSchema(BaseModel):
    rating: int = Field(..., ge=1, le=10)

    model_config = ConfigDict(json_schema_extra={"examples": [movie_rating_schema_example]})


class MovieCommentCreateRequestSchema(BaseModel):
    content: str = Field(..., min_length=1, max_length=5000)
    parent_comment_id: Optional[int] = Field(default=None, gt=0)

    model_config = ConfigDict(
        json_schema_extra={"examples": [movie_comment_create_schema_example]}
    )


class MovieCommentResponseSchema(BaseModel):
    model_config = ConfigDict(
        from_attributes=True, json_schema_extra={"examples": [movie_comment_schema_example]}
    )

    id: int
    movie_id: int
    user_id: int
    parent_comment_id: Optional[int] = None
    content: str
    created_at: datetime
    updated_at: datetime


class MovieCommentNotificationResponseSchema(BaseModel):
    model_config = ConfigDict(
        from_attributes=True, json_schema_extra={"examples": [movie_notification_schema_example]}
    )

    id: int
    recipient_user_id: int
    sender_user_id: int
    comment_id: int
    event_type: str
    is_read: bool
    created_at: datetime


class GenreWithCountResponseSchema(BaseModel):
    model_config = ConfigDict(
        from_attributes=True, json_schema_extra={"examples": [genre_with_count_schema_example]}
    )

    id: int
    name: str
    movies_count: int = Field(..., ge=0)
