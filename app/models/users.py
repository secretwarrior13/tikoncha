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

from app.enums.enums import AppType, Priorities
from app.models.base import SQLModel


class UserTask(SQLModel):

    __tablename__ = "user_tasks"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        nullable=False,
    )
    name = Column(String)
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    type = Column(String)
    priority = Column(
        ENUM(Priorities, name="priorities"),
    )
    scheduled_to = Column(TIMESTAMP)
    user = relationship("User", back_populates="tasks", passive_deletes=True)


class UserRole(SQLModel):
    __tablename__ = "user_roles"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        nullable=False,
    )
    name = Column(String, unique=True, nullable=False)
    policies = relationship(
        "Policy",
        back_populates="role",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    users = relationship("User", back_populates="role")


class User(SQLModel):
    __tablename__ = "users"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        nullable=False,
    )
    username = Column(String, unique=True)
    phone_number = Column(String)
    role_id = Column(
        UUID(as_uuid=True),
        ForeignKey("user_roles.id", ondelete="SET NULL"),
        nullable=True,
    )
    user_role_name = Column(String, nullable=False)

    password_hash = Column(String, nullable=False)

    role = relationship("UserRole", back_populates="users")
    student_info = relationship(
        "StudentInfo",
        foreign_keys="StudentInfo.user_id",
        back_populates="user",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    father_of = relationship(
        "StudentInfo",
        foreign_keys="StudentInfo.father_id",
        back_populates="father_rel",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    mother_of = relationship(
        "StudentInfo",
        foreign_keys="StudentInfo.mother_id",
        back_populates="mother_rel",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    parent_info = relationship(
        "ParentInfo",
        back_populates="user",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    app_requests = relationship(
        "AppRequest",
        foreign_keys="AppRequest.from_user_id",
        back_populates="from_user",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    app_request_logs = relationship(
        "AppRequestLog",
        back_populates="responsible_admin",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    tasks = relationship(
        "UserTask",
        back_populates="user",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    user_devices = relationship(
        "UserDevice",
        back_populates="user",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    setups = relationship(
        "Setup",
        back_populates="user",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    preferences = relationship(
        "UserPreference",
        back_populates="user",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )


class PendingUser(SQLModel):
    __tablename__ = "pending_users"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        nullable=False,
    )
    phone_number = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, nullable=False)
    password_hash = Column(String, nullable=False)
    role_name = Column(String, nullable=False)

    otp_entries = relationship(
        "OTPEntry",
        back_populates="pending_user",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )


class OTPEntry(SQLModel):
    __tablename__ = "otp_entries"

    id = Column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False
    )
    pending_user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("pending_users.id", ondelete="CASCADE"),
        nullable=False,
    )
    phone_number = Column(String, nullable=False, index=True)
    code_hash = Column(String, nullable=False)
    expires_at = Column(TIMESTAMP(timezone=False), nullable=False)
    used = Column(Boolean, default=False, nullable=False)

    pending_user = relationship(
        "PendingUser",
        back_populates="otp_entries",
        passive_deletes=True,
    )
