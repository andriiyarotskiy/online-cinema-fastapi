from __future__ import annotations

import enum
import uuid
from datetime import datetime
from decimal import Decimal
from typing import List, Optional, TYPE_CHECKING

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Column,
    DateTime,
    Enum,
    ForeignKey,
    ForeignKeyConstraint,
    Float,
    Integer,
    Numeric,
    String,
    Table,
    Text,
    UniqueConstraint,
    UUID,
    func,
)
from sqlalchemy.orm import Mapped, relationship, mapped_column

from database import Base, int_pk, str_uniq

if TYPE_CHECKING:
    from database import UserModel


class CertificationEnum(str, enum.Enum):
    G = "G"
    PG = "PG"
    A14 = "A14"
    A18 = "A18"
    R = "R"
    A = "A"
    E = "E"


movie_genres = Table(
    "movie_genres",
    Base.metadata,
    Column("genre_id", ForeignKey("genres.id"), primary_key=True),
    Column("movie_id", ForeignKey("movies.id"), primary_key=True),
)

movie_stars = Table(
    "movie_stars",
    Base.metadata,
    Column("star_id", ForeignKey("stars.id"), primary_key=True),
    Column("movie_id", ForeignKey("movies.id"), primary_key=True),
)

movie_directors = Table(
    "movie_directors",
    Base.metadata,
    Column("director_id", ForeignKey("directors.id"), primary_key=True),
    Column("movie_id", ForeignKey("movies.id"), primary_key=True),
)


class GenreModel(Base):
    __tablename__ = "genres"

    id: Mapped[int_pk]
    name: Mapped[str_uniq] = mapped_column(String(255))

    movies: Mapped[List["MovieModel"]] = relationship(
        secondary=movie_genres, back_populates="genres"
    )

    def __repr__(self):
        return f"<GenreModel(name='{self.name}')>"


class StarModel(Base):
    __tablename__ = "stars"

    id: Mapped[int_pk]
    name: Mapped[str_uniq] = mapped_column(String(255))

    movies: Mapped[List["MovieModel"]] = relationship(
        secondary=movie_stars, back_populates="stars"
    )

    def __repr__(self):
        return f"<StarModel(name='{self.name}')>"


class DirectorModel(Base):
    __tablename__ = "directors"

    id: Mapped[int_pk]
    name: Mapped[str_uniq] = mapped_column(String(255))

    movies: Mapped[List["MovieModel"]] = relationship(
        secondary=movie_directors, back_populates="directors"
    )

    def __repr__(self):
        return f"<DirectorModel(name='{self.name}')>"


class CertificationModel(Base):
    __tablename__ = "certifications"
    id: Mapped[int_pk]

    name: Mapped[CertificationEnum] = mapped_column(
        Enum(
            CertificationEnum,
            name="certificationenum",
            validate_strings=True,
            create_type=False,
        ),
        unique=True,
    )
    movies: Mapped[List["MovieModel"]] = relationship(
        back_populates="certification",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    def __repr__(self):
        return f"<CertificationModel(name='{self.name}')>"


class MovieVoteModel(Base):
    __tablename__ = "movie_votes"

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), primary_key=True
    )
    movie_id: Mapped[int] = mapped_column(
        ForeignKey("movies.id", ondelete="CASCADE"), primary_key=True
    )

    is_liked: Mapped[bool]
    user: Mapped["UserModel"] = relationship("UserModel", back_populates="movie_votes")
    movie: Mapped["MovieModel"] = relationship(
        "MovieModel", back_populates="user_votes"
    )


class FavoriteMovieModel(Base):
    __tablename__ = "favorite_movies"

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), primary_key=True
    )
    movie_id: Mapped[int] = mapped_column(
        ForeignKey("movies.id", ondelete="CASCADE"), primary_key=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    user: Mapped["UserModel"] = relationship(
        "UserModel", back_populates="favorite_movies"
    )
    movie: Mapped["MovieModel"] = relationship("MovieModel", back_populates="favorites")


class MovieRatingModel(Base):
    __tablename__ = "movie_ratings"
    __table_args__ = (
        CheckConstraint("rating >= 1 AND rating <= 10", name="movie_rating_range"),
    )

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), primary_key=True
    )
    movie_id: Mapped[int] = mapped_column(
        ForeignKey("movies.id", ondelete="CASCADE"), primary_key=True
    )
    rating: Mapped[int] = mapped_column(Integer, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    user: Mapped["UserModel"] = relationship(
        "UserModel", back_populates="movie_ratings"
    )
    movie: Mapped["MovieModel"] = relationship("MovieModel", back_populates="ratings")


class MoviePurchaseModel(Base):
    __tablename__ = "movie_purchases"

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), primary_key=True
    )
    movie_id: Mapped[int] = mapped_column(
        ForeignKey("movies.id", ondelete="RESTRICT"), primary_key=True
    )
    purchased_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    price_paid: Mapped[Decimal] = mapped_column(Numeric(precision=10, scale=2))

    user: Mapped["UserModel"] = relationship(
        "UserModel", back_populates="movie_purchases"
    )
    movie: Mapped["MovieModel"] = relationship("MovieModel", back_populates="purchases")


class MovieCommentModel(Base):
    __tablename__ = "movie_comments"

    id: Mapped[int_pk]
    movie_id: Mapped[int] = mapped_column(
        ForeignKey("movies.id", ondelete="CASCADE"), nullable=False
    )
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    parent_comment_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("movie_comments.id", ondelete="CASCADE"), nullable=True
    )
    content: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    movie: Mapped["MovieModel"] = relationship("MovieModel", back_populates="comments")
    user: Mapped["UserModel"] = relationship(
        "UserModel", back_populates="movie_comments"
    )
    parent_comment: Mapped[Optional["MovieCommentModel"]] = relationship(
        "MovieCommentModel",
        remote_side="MovieCommentModel.id",
        back_populates="replies",
    )
    replies: Mapped[List["MovieCommentModel"]] = relationship(
        "MovieCommentModel",
        back_populates="parent_comment",
        cascade="all, delete-orphan",
    )
    likes: Mapped[List["MovieCommentLikeModel"]] = relationship(
        "MovieCommentLikeModel",
        back_populates="comment",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    received_notifications: Mapped[List["MovieCommentNotificationModel"]] = (
        relationship(
            "MovieCommentNotificationModel",
            back_populates="comment",
            cascade="all, delete-orphan",
            passive_deletes=True,
        )
    )


class MovieCommentLikeModel(Base):
    __tablename__ = "movie_comment_likes"

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), primary_key=True
    )
    comment_id: Mapped[int] = mapped_column(
        ForeignKey("movie_comments.id", ondelete="CASCADE"), primary_key=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    user: Mapped["UserModel"] = relationship(
        "UserModel", back_populates="movie_comment_likes"
    )
    comment: Mapped["MovieCommentModel"] = relationship(
        "MovieCommentModel", back_populates="likes"
    )
    generated_notifications: Mapped[List["MovieCommentNotificationModel"]] = (
        relationship(
            "MovieCommentNotificationModel",
            back_populates="comment_like",
        )
    )


class MovieCommentNotificationTypeEnum(str, enum.Enum):
    REPLY = "reply"
    LIKE = "like"


class MovieCommentNotificationModel(Base):
    __tablename__ = "movie_comment_notifications"
    __table_args__ = (
        ForeignKeyConstraint(
            ["comment_like_user_id", "comment_like_comment_id"],
            ["movie_comment_likes.user_id", "movie_comment_likes.comment_id"],
            name="fk_movie_comment_notifications_comment_like",
            ondelete="CASCADE",
        ),
    )

    id: Mapped[int_pk]
    recipient_user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    sender_user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    comment_id: Mapped[int] = mapped_column(
        ForeignKey("movie_comments.id", ondelete="CASCADE"), nullable=False
    )
    comment_like_user_id: Mapped[Optional[int]] = mapped_column(nullable=True)
    comment_like_comment_id: Mapped[Optional[int]] = mapped_column(nullable=True)
    event_type: Mapped[MovieCommentNotificationTypeEnum] = mapped_column(
        Enum(
            MovieCommentNotificationTypeEnum,
            name="moviecommentnotificationtypeenum",
            validate_strings=True,
            create_type=False,
        ),
        nullable=False,
    )
    is_read: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    user: Mapped["UserModel"] = relationship(
        "UserModel",
        foreign_keys=[recipient_user_id],
        back_populates="movie_comment_notifications",
    )
    sender: Mapped["UserModel"] = relationship(
        "UserModel",
        foreign_keys=[sender_user_id],
        back_populates="sent_movie_comment_notifications",
    )
    comment: Mapped["MovieCommentModel"] = relationship(
        "MovieCommentModel", back_populates="received_notifications"
    )
    comment_like: Mapped[Optional["MovieCommentLikeModel"]] = relationship(
        "MovieCommentLikeModel",
        foreign_keys=[comment_like_user_id, comment_like_comment_id],
        back_populates="generated_notifications",
    )


class MovieModel(Base):
    __tablename__ = "movies"

    id: Mapped[int_pk]

    user_votes: Mapped[List["MovieVoteModel"]] = relationship(
        "MovieVoteModel",
        back_populates="movie",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    favorites: Mapped[List["FavoriteMovieModel"]] = relationship(
        "FavoriteMovieModel",
        back_populates="movie",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    ratings: Mapped[List["MovieRatingModel"]] = relationship(
        "MovieRatingModel",
        back_populates="movie",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    comments: Mapped[List["MovieCommentModel"]] = relationship(
        "MovieCommentModel",
        back_populates="movie",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    purchases: Mapped[List["MoviePurchaseModel"]] = relationship(
        "MoviePurchaseModel",
        back_populates="movie",
        passive_deletes=True,
    )

    uuid: Mapped[uuid.UUID] = mapped_column(UUID, unique=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    year: Mapped[int] = mapped_column(Integer, nullable=False)
    time: Mapped[int] = mapped_column(Integer, nullable=False)
    imdb: Mapped[float] = mapped_column(Float, nullable=False)
    votes: Mapped[int] = mapped_column(Integer, nullable=False)
    meta_score: Mapped[Optional[float]] = mapped_column(Float)
    gross: Mapped[Optional[float]] = mapped_column(Float)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    price: Mapped[Decimal] = mapped_column(
        Numeric(precision=10, scale=2), nullable=False
    )

    __table_args__ = (
        UniqueConstraint(
            "name",
            "year",
            "time",
            name="name_year_time_uniqueness",
        ),
    )

    certification_id: Mapped[int] = mapped_column(
        ForeignKey("certifications.id", ondelete="CASCADE")
    )
    certification: Mapped["CertificationModel"] = relationship(
        "CertificationModel", back_populates="movies"
    )

    genres: Mapped[List[GenreModel]] = relationship(
        secondary=movie_genres, back_populates="movies"
    )

    stars: Mapped[List[StarModel]] = relationship(
        secondary=movie_stars, back_populates="movies"
    )

    directors: Mapped[List[DirectorModel]] = relationship(
        secondary=movie_directors, back_populates="movies"
    )

    def __repr__(self):
        return (
            f"<MovieModel(name='{self.name}', "
            f"year={self.year}, "
            f"time={self.time})>"
        )
