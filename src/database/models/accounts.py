from __future__ import annotations

import enum
from typing import TYPE_CHECKING, List, Optional
from datetime import datetime, timezone, timedelta

from sqlalchemy import (
    Integer,
    Enum,
    String,
    Boolean,
    DateTime,
    func,
    ForeignKey,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship, validates

from database import Base, str_uniq
from database.validators import accounts as validators
from security.passwords import hash_password, verify_password
from security.utils import generate_secure_token

if TYPE_CHECKING:
    from database import (
        FavoriteMovieModel,
        MovieCommentLikeModel,
        MovieCommentModel,
        MovieCommentNotificationModel,
        MoviePurchaseModel,
        MovieRatingModel,
        MovieVoteModel,
        UserProfileModel,
    )


class UserGroupEnum(str, enum.Enum):
    USER = "user"
    MODERATOR = "moderator"
    ADMIN = "admin"


class UserGroupModel(Base):
    __tablename__ = "user_groups"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[UserGroupEnum] = mapped_column(Enum(UserGroupEnum), unique=True)

    users: Mapped[List["UserModel"]] = relationship(
        "UserModel",
        back_populates="group",
    )

    def __repr__(self) -> str:
        return f"<UserGroupModel(id={self.id}, name={self.name})>"


class UserModel(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str_uniq]
    _hashed_password: Mapped[str] = mapped_column("hashed_password", String(255))
    is_active: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    group_id: Mapped[int] = mapped_column(ForeignKey("user_groups.id"))
    group: Mapped["UserGroupModel"] = relationship(back_populates="users")

    profile: Mapped[Optional["UserProfileModel"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
    activation_token: Mapped[Optional["ActivationTokenModel"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
    password_reset_token: Mapped[Optional["PasswordResetTokenModel"]] = relationship(
        "PasswordResetTokenModel", back_populates="user", cascade="all, delete-orphan"
    )

    refresh_tokens: Mapped[List["RefreshTokenModel"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
    movie_votes: Mapped[List["MovieVoteModel"]] = relationship(
        "MovieVoteModel",
        back_populates="user",
        cascade="all, delete-orphan",
    )
    favorite_movies: Mapped[List["FavoriteMovieModel"]] = relationship(
        "FavoriteMovieModel",
        back_populates="user",
        cascade="all, delete-orphan",
    )
    movie_ratings: Mapped[List["MovieRatingModel"]] = relationship(
        "MovieRatingModel",
        back_populates="user",
        cascade="all, delete-orphan",
    )
    movie_purchases: Mapped[List["MoviePurchaseModel"]] = relationship(
        "MoviePurchaseModel",
        back_populates="user",
        cascade="all, delete-orphan",
    )
    movie_comments: Mapped[List["MovieCommentModel"]] = relationship(
        "MovieCommentModel",
        back_populates="user",
        cascade="all, delete-orphan",
    )
    movie_comment_likes: Mapped[List["MovieCommentLikeModel"]] = relationship(
        "MovieCommentLikeModel",
        back_populates="user",
        cascade="all, delete-orphan",
    )
    movie_comment_notifications: Mapped[List["MovieCommentNotificationModel"]] = (
        relationship(
            "MovieCommentNotificationModel",
            foreign_keys="MovieCommentNotificationModel.recipient_user_id",
            back_populates="user",
            cascade="all, delete-orphan",
        )
    )
    sent_movie_comment_notifications: Mapped[List["MovieCommentNotificationModel"]] = (
        relationship(
            "MovieCommentNotificationModel",
            foreign_keys="MovieCommentNotificationModel.sender_user_id",
            back_populates="sender",
        )
    )

    @classmethod
    def create(
        cls, email: str, raw_password: str, group_id: int | Mapped[int]
    ) -> "UserModel":
        """
        Factory method to create a new UserModel instance.

        This method simplifies the creation of a new user by handling
        password hashing and setting required attributes.
        """
        user = cls(email=email, group_id=group_id)
        user.password = raw_password
        return user

    @property
    def password(self) -> None:
        raise AttributeError(
            "Password is write-only. Use the setter to set the password."
        )

    @password.setter
    def password(self, raw_password: str) -> None:
        """
        Set the user's password after validating its strength and hashing it.
        """
        validators.validate_password_strength(raw_password)
        self._hashed_password = hash_password(raw_password)

    def verify_password(self, raw_password: str) -> bool:
        """
        Verify the provided password against the stored hashed password.
        """
        return verify_password(raw_password, self._hashed_password)

    @validates("email")
    def validate_email(self, key, value):
        return validators.validate_email(value.lower())

    def __repr__(self) -> str:
        return (
            f"<UserModel(id={self.id}, email={self.email}), is_active={self.is_active}>"
        )


class TokenBaseModel(Base):
    __abstract__ = True

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    token: Mapped[str] = mapped_column(
        String(64), unique=True, default=generate_secure_token
    )
    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc) + timedelta(days=1),
    )

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))


class ActivationTokenModel(TokenBaseModel):
    __tablename__ = "activation_tokens"

    user: Mapped[UserModel] = relationship(back_populates="activation_token")

    __table_args__ = (UniqueConstraint("user_id"),)

    def __repr__(self):
        return f"<ActivationTokenModel(id={self.id}, token={self.token}, expires_at={self.expires_at})>"


class PasswordResetTokenModel(TokenBaseModel):
    __tablename__ = "password_reset_tokens"

    user: Mapped[UserModel] = relationship(back_populates="password_reset_token")

    __table_args__ = (UniqueConstraint("user_id"),)

    def __repr__(self) -> str:
        return f"<PasswordResetTokenModel(id={self.id}, token={self.token}, expires_at={self.expires_at})>"


class RefreshTokenModel(TokenBaseModel):
    __tablename__ = "refresh_tokens"

    token: Mapped[str] = mapped_column(
        String(512), unique=True, default=generate_secure_token
    )

    user: Mapped[UserModel] = relationship(back_populates="refresh_tokens")

    @classmethod
    def create(
        cls, user_id: int | Mapped[int], days_valid: int, token: str
    ) -> "RefreshTokenModel":
        """
        Factory method to create a new RefreshTokenModel instance.

        This method simplifies the creation of a new refresh token by calculating
        the expiration date based on the provided number of valid days and setting
        the required attributes.
        """
        expires_at = datetime.now(timezone.utc) + timedelta(days=days_valid)
        return cls(user_id=user_id, expires_at=expires_at, token=token)

    def __repr__(self):
        return f"<RefreshTokenModel(id={self.id}, token={self.token}, expires_at={self.expires_at})>"
