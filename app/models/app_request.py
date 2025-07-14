import uuid
<<<<<<< HEAD
=======

from sqlalchemy import Column, ForeignKey, Text
from sqlalchemy.dialects.postgresql import ENUM, UUID
from sqlalchemy.orm import relationship
>>>>>>> 1e6f4b61bd2dc388852b3f1b09697b0a276db0c0

from sqlalchemy import (
    JSON,
    TIMESTAMP,
    Boolean,
    Column,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
    func,
)
from sqlalchemy.dialects.postgresql import ENUM, UUID
from sqlalchemy.orm import relationship

from app.enums.enums import AppRequestStatuses, AppType
from app.models.base import SQLModel


class AppRequest(SQLModel):

    __tablename__ = "app_requests"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        nullable=False,
    )
    app_id = Column(
        UUID(as_uuid=True),
        ForeignKey("apps.id", ondelete="CASCADE"),
        nullable=False,
    )
    from_user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    reason = Column(Text)
    status = Column(
        ENUM(AppRequestStatuses, name="app_request_statuses"),
        server_default=AppRequestStatuses.PENDING.value,
        default=AppRequestStatuses.PENDING.value,
        nullable=False,
    )
    app = relationship("App", back_populates="app_requests")
    from_user = relationship(
        "User",
        foreign_keys=[from_user_id],
        back_populates="app_requests",
        passive_deletes=True,
    )
    logs = relationship(
        "AppRequestLog",
        back_populates="app_request",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )


class AppRequestLog(SQLModel):
    __tablename__ = "app_requests_logs"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        nullable=False,
    )
    app_request_id = Column(
        UUID(as_uuid=True),
        ForeignKey("app_requests.id", ondelete="CASCADE"),
        nullable=False,
    )
    status_was = Column(
        ENUM(AppRequestStatuses, name="app_request_status_was"),
        nullable=False,
    )
    status_changed_to = Column(
        ENUM(AppRequestStatuses, name="app_request_status_changed_to"),
        nullable=False,
    )
    responsible_admin_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=True,
    )
    basis = Column(Text)

    app_request = relationship(
        "AppRequest",
        back_populates="logs",
        passive_deletes=True,
    )
    responsible_admin = relationship(
        "User",
        back_populates="app_request_logs",
        passive_deletes=True,
    )


class App(SQLModel):
    __tablename__ = "apps"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        nullable=False,
    )
    name = Column(String, nullable=False)
    package = Column(String, unique=True)
    icon = Column(String)
    install_count = Column(Integer, default=0)
    type = Column(
        ENUM(AppType, name="app_type"),
    )
    added_at = Column(TIMESTAMP, nullable=False, server_default=func.now())

    policy_apps = relationship("PolicyApp", back_populates="app")
    app_requests = relationship(
        "AppRequest",
        back_populates="app",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    user_apps = relationship("UserApp", back_populates="app")
