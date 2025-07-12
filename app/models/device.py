from sqlalchemy import Column, Integer, String, TIMESTAMP, ForeignKey, Boolean, func
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import ENUM
from app.enums.enums import OsTypes, AndroidUI, PhoneBrands, ActionDegrees
from app.models.base import SQLModel
import uuid
from sqlalchemy.dialects.postgresql import UUID


class OS(SQLModel):

    __tablename__ = "operating_systems"
    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        nullable=False,
    )
    type = Column(
        ENUM(OsTypes, name="os_types"),
        nullable=False,
    )
    version = Column(String)
    ui = Column(
        ENUM(AndroidUI, name="android_ui"),
        nullable=True,
    )
    ui_version = Column(String)

    devices = relationship(
        "Device",
        back_populates="os",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )


class Device(SQLModel):

    __tablename__ = "devices"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        nullable=False,
    )
    brand = Column(
        ENUM(PhoneBrands, name="phone_brands"),
    )
    model = Column(String)
    os_id = Column(
        UUID(as_uuid=True),
        ForeignKey("operating_systems.id", ondelete="CASCADE"),
        nullable=False,
    )
    ram = Column(Integer)
    storage = Column(Integer)
    IMEI = Column(String)

    # Relationships
    os = relationship("OS", back_populates="devices")
    user_devices = relationship(
        "UserDevice",
        back_populates="device",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )


class UserDevice(SQLModel):
    __tablename__ = "user_devices"

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
    device_id = Column(
        UUID(as_uuid=True),
        ForeignKey("devices.id", ondelete="CASCADE"),
        nullable=False,
    )

    user = relationship(
        "User",
        back_populates="user_devices",
        passive_deletes=True,
    )
    device = relationship(
        "Device",
        back_populates="user_devices",
        passive_deletes=True,
    )
    logs = relationship(
        "Log",
        back_populates="user_device",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    setups = relationship("Setup", back_populates="user_device")
    user_apps = relationship("UserApp", back_populates="user_device")


class Action(SQLModel):

    __tablename__ = "actions"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        nullable=False,
    )
    name = Column(String, nullable=False, unique=True)
    degree = Column(
        ENUM(ActionDegrees, name="action_degrees"),
    )
    logs = relationship(
        "Log",
        back_populates="action",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )


class Log(SQLModel):

    __tablename__ = "logs"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        nullable=False,
    )
    user_device_id = Column(
        UUID(as_uuid=True),
        ForeignKey("user_devices.id", ondelete="CASCADE"),
        nullable=False,
    )
    user_app_id = Column(
        UUID(as_uuid=True),
        ForeignKey("user_apps.id", ondelete="CASCADE"),
        nullable=True,
    )
    action_id = Column(
        UUID(as_uuid=True),
        ForeignKey("actions.id", ondelete="CASCADE"),
        nullable=False,
    )
    done_at = Column(TIMESTAMP, nullable=False, server_default=func.now())
    location = Column(String)
    details = Column(String)

    user_device = relationship(
        "UserDevice",
        back_populates="logs",
        cascade="none",
        passive_deletes=True,
    )
    user_app = relationship(
        "UserApp",
        back_populates="logs",
        passive_deletes=True,
    )
    action = relationship(
        "Action",
        back_populates="logs",
        passive_deletes=True,
    )


class Setup(SQLModel):

    __tablename__ = "setups"

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
    user_device_id = Column(
        UUID(as_uuid=True),
        ForeignKey("user_devices.id", ondelete="CASCADE"),
        nullable=False,
    )
    camera = Column(Boolean)
    location = Column(Boolean)
    usage_access = Column(Boolean)
    admin_app = Column(Boolean)
    accessibility_features = Column(Boolean)
    pop_up = Column(Boolean)
    notification_service = Column(Boolean)
    battery_optimization = Column(Boolean)
    gps = Column(Boolean)

    user = relationship(
        "User",
        back_populates="setups",
        passive_deletes=True,
    )
    user_device = relationship(
        "UserDevice",
        back_populates="setups",
        passive_deletes=True,
    )


class UserApp(SQLModel):

    __tablename__ = "user_apps"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        nullable=False,
    )
    user_device_id = Column(
        UUID(as_uuid=True),
        ForeignKey("user_devices.id", ondelete="CASCADE"),
        nullable=False,
    )
    app_id = Column(
        UUID(as_uuid=True),
        ForeignKey("apps.id", ondelete="CASCADE"),
        nullable=False,
    )
    added_at = Column(TIMESTAMP, nullable=False, server_default=func.now())
    is_active = Column(Boolean, default=True)

    user_device = relationship(
        "UserDevice",
        back_populates="user_apps",
        passive_deletes=True,
    )
    app = relationship(
        "App",
        back_populates="user_apps",
        passive_deletes=True,
    )
    logs = relationship(
        "Log",
        back_populates="user_app",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
