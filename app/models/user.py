from sqlalchemy import (
    Column,
    Integer,
    String,
    TIMESTAMP,
    ForeignKey,
    Boolean,
    Text,
    Numeric,
    JSON,
    func,
    UniqueConstraint,
    Index,
)
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import ENUM

from app.models.base import SQLModel
from app.enums.enums import (
    Priorities,
    Genders,
    Shifts,
    OsTypes,
    AndroidUI,
    PhoneBrands,
    ActionDegrees,
    Languages,
    Themes,
    AppType,
    AppRequestStatuses,
    GeneralType,
)
import uuid
from sqlalchemy.dialects.postgresql import UUID


class UserTask(SQLModel):
    """User tasks model"""

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


class UserType(SQLModel):

    __tablename__ = "user_types"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        nullable=False,
    )
    name = Column(String, nullable=False)
    user_level = Column(Integer)
    school = Column(
        UUID(as_uuid=True),
        ForeignKey("schools.id", ondelete="CASCADE"),
        nullable=False,
    )
    users = relationship("User", back_populates="user_type_rel")
    school_rel = relationship("School", back_populates="user_types")
    policies = relationship("Policy", back_populates="targeted_user_type")


class Website(SQLModel):
    """Website model"""

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
    targeted_user_type_id = Column(
        UUID(as_uuid=True),
        ForeignKey("user_types.id", ondelete="CASCADE"),
        nullable=False,
    )

    targeted_user_type = relationship("UserType", back_populates="policies")
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


class Region(SQLModel):

    __tablename__ = "regions"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        nullable=False,
    )
    name = Column(String, unique=True)

    cities = relationship(
        "City",
        back_populates="region",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
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


class City(SQLModel):
    """City model"""

    __tablename__ = "cities"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        nullable=False,
    )
    name = Column(String, unique=True)
    parent_region = Column(
        UUID(as_uuid=True),
        ForeignKey("regions.id", ondelete="CASCADE"),
        nullable=False,
    )
    region = relationship("Region", back_populates="cities")
    schools = relationship(
        "School",
        back_populates="city_rel",
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
    parent_region = Column(
        UUID(as_uuid=True),
        ForeignKey("regions.id", ondelete="CASCADE"),
        nullable=False,
    )
    region = relationship("Region", back_populates="districts")
    schools = relationship("School", back_populates="district_rel")


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
    region = Column(
        UUID(as_uuid=True),
        ForeignKey("regions.id", ondelete="CASCADE"),
        nullable=False,
    )
    city = Column(
        UUID(as_uuid=True),
        ForeignKey("cities.id", ondelete="CASCADE"),
        nullable=False,
    )
    district = Column(
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
        nullable=False,
    )
    region_rel = relationship("Region", back_populates="schools")
    city_rel = relationship(
        "City",
        back_populates="schools",
        passive_deletes=True,
    )
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
    user_types = relationship(
        "UserType",
        back_populates="school_rel",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    student_infos = relationship(
        "StudentInfo",
        back_populates="school_rel",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )


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
    user_type_id = Column(
        UUID(as_uuid=True),
        ForeignKey("user_types.id", ondelete="CASCADE"),
        nullable=True,
    )
    user_role_name = Column(String, nullable=False)

    password_hash = Column(String, nullable=False)

    user_type_rel = relationship("UserType", back_populates="users")
    student_info = relationship(
        "StudentInfo",
        foreign_keys="StudentInfo.user_id",
        back_populates="user",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    father_of = relationship(
        "StudentInfo",
        foreign_keys="StudentInfo.father",
        back_populates="father_rel",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    mother_of = relationship(
        "StudentInfo",
        foreign_keys="StudentInfo.mother",
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
    school = Column(
        UUID(as_uuid=True),
        ForeignKey("schools.id", ondelete="CASCADE"),
        nullable=False,
    )
    shift = Column(
        ENUM(Shifts, name="shifts"),
    )
    father = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=True,
    )
    mother = Column(
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
        foreign_keys=[father],
        back_populates="father_of",
        passive_deletes=True,
    )
    mother_rel = relationship(
        "User",
        foreign_keys=[mother],
        back_populates="mother_of",
        passive_deletes=True,
    )


class ParentInfo(SQLModel):

    __tablename__ = "parent_infos"

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
    passport_id = Column(String)

    user = relationship(
        "User",
        back_populates="parent_info",
        passive_deletes=True,
    )
