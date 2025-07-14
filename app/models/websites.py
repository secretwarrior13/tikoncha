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

from app.models.base import SQLModel


class Website(SQLModel):

    __tablename__ = "websites"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        nullable=False,
    )
    domain = Column(String, nullable=False, unique=True)
    icon = Column(String)
    visit_count = Column(Integer, default=0)
    type = Column(String)
    added_at = Column(TIMESTAMP, nullable=False, server_default=func.now())

    policy_webs = relationship(
        "PolicyWeb",
        back_populates="website",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
