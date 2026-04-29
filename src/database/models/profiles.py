from __future__ import annotations

import enum
from datetime import datetime
from typing import Optional, TYPE_CHECKING

from sqlalchemy import Integer, String, Enum, Date, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database import Base

if TYPE_CHECKING:
    from database import UserModel


class GenderEnum(str, enum.Enum):
    MAN = "man"
    WOMAN = "woman"


class UserProfileModel(Base):
    __tablename__ = "user_profiles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    first_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    last_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    avatar: Mapped[Optional[str]] = mapped_column(nullable=True)
    gender: Mapped[Optional[GenderEnum]] = mapped_column(
        Enum(GenderEnum), nullable=True
    )
    date_of_birth: Mapped[Optional[datetime.date]] = mapped_column(Date, nullable=True)
    info: Mapped[Optional[str]] = mapped_column(Text)

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), unique=True
    )

    user: Mapped["UserModel"] = relationship(back_populates="profile")

    def __repr__(self) -> str:
        return (
            f"<UserProfileModel(id={self.id}, "
            f"first_name={self.first_name} "
            f"last_name={self.last_name})>"
        )
