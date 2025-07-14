import uuid

from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.models.base import SQLModel


class Policy(SQLModel):
    __tablename__ = "policies"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        nullable=False,
    )
    name = Column(String, nullable=False)
    is_whitelist_app = Column(Boolean, default=True)
    is_whitelist_web = Column(Boolean, default=True)
    targeted_role_id = Column(
        UUID(as_uuid=True),
        ForeignKey("user_roles.id", ondelete="CASCADE"),
        nullable=False,
    )
    role = relationship("UserRole", back_populates="policies")
    policy_apps = relationship(
        "PolicyApp",
        back_populates="policy",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    policy_webs = relationship(
        "PolicyWeb",
        back_populates="policy",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    schools = relationship(
        "School",
        back_populates="policy",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )


class PolicyApp(SQLModel):
    __tablename__ = "policy_apps"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        nullable=False,
    )
    policy_id = Column(
        UUID(as_uuid=True),
        ForeignKey("policies.id", ondelete="CASCADE"),
        nullable=False,
    )
    app_id = Column(
        UUID(as_uuid=True),
        ForeignKey("apps.id", ondelete="CASCADE"),
        nullable=False,
    )
    duration = Column(Integer)

    policy = relationship("Policy", back_populates="policy_apps")
    app = relationship("App", back_populates="policy_apps")


class PolicyWeb(SQLModel):
    __tablename__ = "policy_webs"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        nullable=False,
    )
    policy_id = Column(
        UUID(as_uuid=True),
        ForeignKey("policies.id", ondelete="CASCADE"),
        nullable=False,
    )
    website_id = Column(
        UUID(as_uuid=True),
        ForeignKey("websites.id", ondelete="CASCADE"),
        nullable=False,
    )
    duration = Column(Integer)

    policy = relationship("Policy", back_populates="policy_webs")
    website = relationship("Website", back_populates="policy_webs")
