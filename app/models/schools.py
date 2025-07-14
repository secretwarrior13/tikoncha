import uuid

from sqlalchemy import JSON, Column, ForeignKey, Numeric, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.models.base import SQLModel


class School(SQLModel):
    """School model"""

    __tablename__ = "schools"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        nullable=False,
    )
    name = Column(String, nullable=False)
    region_id = Column(
        UUID(as_uuid=True),
        ForeignKey("regions.id", ondelete="CASCADE"),
        nullable=False,
    )

    district_id = Column(
        UUID(as_uuid=True),
        ForeignKey("districts.id", ondelete="CASCADE"),
        nullable=False,
    )
    address = Column(String)
    latitude = Column(Numeric(10, 8))
    longitude = Column(Numeric(11, 8))
    location = Column(JSON)
    radius = Column(Numeric)
    policy_id = Column(
        UUID(as_uuid=True),
        ForeignKey("policies.id", ondelete="CASCADE"),
        nullable=True,
    )
    region_rel = relationship("Region", back_populates="schools")

    district_rel = relationship(
        "District",
        back_populates="schools",
        passive_deletes=True,
    )
    policy = relationship(
        "Policy",
        back_populates="schools",
        passive_deletes=True,
    )
    student_infos = relationship(
        "StudentInfo",
        back_populates="school_rel",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
