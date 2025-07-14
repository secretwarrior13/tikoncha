import uuid

from sqlalchemy import Column, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.models.base import SQLModel


class Region(SQLModel):
    __tablename__ = "regions"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        nullable=False,
    )
    name = Column(String, unique=True)
    coordinate = Column(String, nullable=True)

    districts = relationship(
        "District",
        back_populates="region",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    schools = relationship(
        "School",
        back_populates="region_rel",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )


class District(SQLModel):
    __tablename__ = "districts"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        nullable=False,
    )
    name = Column(String, unique=True)
    coordinate = Column(String, nullable=True)

    parent_region = Column(
        UUID(as_uuid=True),
        ForeignKey("regions.id", ondelete="CASCADE"),
        nullable=False,
    )
    region = relationship("Region", back_populates="districts")
    schools = relationship("School", back_populates="district_rel")
