import uuid
from decimal import Decimal
from typing import List, Optional

from sqlalchemy import (
    String,
    Column,
    ForeignKey,
    Table,
    UUID,
    Integer,
    Float,
    Text,
    Numeric,
    UniqueConstraint,
    Uuid,
)
from sqlalchemy.orm import Mapped, relationship, mapped_column

from database import Base, int_pk, str_uniq

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

    name: Mapped[str_uniq] = mapped_column(String(64))
    movies: Mapped[List["MovieModel"]] = relationship(
        back_populates="certification",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    def __repr__(self):
        return f"<CertificationModel(name='{self.name}')>"


class MovieModel(Base):
    __tablename__ = "movies"

    id: Mapped[int_pk]
    uuid: Mapped[Uuid] = mapped_column(UUID, unique=True, default=uuid.uuid4)
    name: Mapped[str_uniq] = mapped_column(String(255))
    year: Mapped[int] = mapped_column(Integer)
    time: Mapped[int] = mapped_column(Integer)
    imdb: Mapped[float] = mapped_column(Float)
    votes: Mapped[int] = mapped_column(Integer)
    meta_score: Mapped[Optional[float]] = mapped_column(Float)
    gross: Mapped[Optional[float]] = mapped_column(Float)
    description: Mapped[str] = mapped_column(Text)
    price: Mapped[Decimal] = mapped_column(Numeric(precision=10, scale=2))

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
