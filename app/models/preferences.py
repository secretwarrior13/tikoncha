import uuid

from sqlalchemy import Column, ForeignKey
from sqlalchemy.dialects.postgresql import ENUM, UUID
from sqlalchemy.orm import relationship

from app.enums.enums import Languages, Themes
from app.models.base import SQLModel


class UserPreference(SQLModel):
    """User Preferences model"""

    __tablename__ = "user_preferences"

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
    language = Column(
        ENUM(Languages, name="languages"),
        nullable=True,
    )
    theme = Column(
        ENUM(Themes, name="themes"),
        nullable=True,
    )
    # Relationships
    user = relationship(
        "User",
        back_populates="preferences",
        passive_deletes=True,
    )
