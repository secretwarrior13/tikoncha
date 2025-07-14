import uuid

from sqlalchemy import (
    JSON,
    TIMESTAMP,
    Boolean,
    Column,
    ForeignKey,
    Integer,
    Numeric,
    String,
    func,
)
from sqlalchemy.dialects.postgresql import ENUM, UUID
from sqlalchemy.orm import relationship

from app.enums.enums import AppType, Genders, Priorities, Shifts
from app.models.base import SQLModel


class StudentInfo(SQLModel):
    __tablename__ = "student_infos"

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
    school_id = Column(
        UUID(as_uuid=True),
        ForeignKey("schools.id", ondelete="CASCADE"),
        nullable=False,
    )
    shift = Column(
        ENUM(Shifts, name="shifts"),
    )
    father_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=True,
    )
    mother_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=True,
    )
    user = relationship(
        "User",
        foreign_keys=[user_id],
        back_populates="student_info",
        passive_deletes=True,
    )
    school_rel = relationship(
        "School",
        back_populates="student_infos",
        passive_deletes=True,
    )
    father_rel = relationship(
        "User",
        foreign_keys=[father_id],
        back_populates="father_of",
        passive_deletes=True,
    )
    mother_rel = relationship(
        "User",
        foreign_keys=[mother_id],
        back_populates="mother_of",
        passive_deletes=True,
    )
