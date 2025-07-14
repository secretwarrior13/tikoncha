import uuid

from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import ENUM, UUID
from sqlalchemy.orm import relationship

from app.enums.enums import Genders
from app.models.base import SQLModel


class ParentInfo(SQLModel):
    __tablename__ = "parent_infos"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        nullable=False,
    )
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    first_name = Column(String)
    last_name = Column(String)
    patronymic = Column(String)
    age = Column(Integer)
    gender = Column(
        ENUM(Genders, name="genders"),
    )
    passport_id = Column(String)

    user = relationship(
        "User",
        back_populates="parent_info",
        passive_deletes=True,
    )
