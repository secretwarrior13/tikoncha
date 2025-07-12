from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import ENUM

from app.models.base import SQLModel
from app.enums.enums import Languages, Themes
import uuid
from sqlalchemy.dialects.postgresql import UUID


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
