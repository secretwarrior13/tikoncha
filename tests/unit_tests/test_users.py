import hashlib
from datetime import datetime, timedelta
from types import SimpleNamespace
from uuid import UUID, uuid4

import pytest
from fastapi import HTTPException, status
from unittest.mock import AsyncMock, MagicMock

from app.services.users import UserService
from app.enums.enums import UserRole
from app.schemas.users import UserCreateRequest, UserUpdate


def _scalar_result(obj):
    scalars = MagicMock()
    scalars.first.return_value = obj
    res = MagicMock()
    res.scalars.return_value = scalars
    return res


def _user(phone="+998900000000", role=UserRole.STUDENT, **kw):
    base = dict(
        id=uuid4(),
        phone_number=phone,
        username="tester",
        password_hash="hashed",
        user_role_name=role.value,
    )
    base.update(kw)
    return SimpleNamespace(**base)


@pytest.fixture
def mock_session():
    s = MagicMock()
    s.execute = AsyncMock()
    s.commit = AsyncMock()
    s.flush = AsyncMock()
    s.refresh = AsyncMock()
    s.delete = AsyncMock()
    s.rollback = AsyncMock()
    s.add = MagicMock()
    return s


@pytest.fixture
def user_service(mock_session):
    return UserService(db=mock_session)


@pytest.mark.asyncio
async def test_check_user_exists_happy_path(user_service, mock_session):
    u = _user()
    mock_session.execute.return_value = _scalar_result(u)
    r = await user_service.check_user_exists(u.phone_number)
    assert r.exists is True
    mock_session.execute.assert_awaited_once()


@pytest.mark.asyncio
async def test_check_user_exists_not_found(user_service, mock_session):
    mock_session.execute.return_value = _scalar_result(None)
    with pytest.raises(HTTPException):
        await user_service.check_user_exists("+1")


@pytest.mark.asyncio
async def test_get_user_profile_current_user(user_service, mock_session):
    u = _user()
    mock_session.execute.return_value = _scalar_result(u)
    assert await user_service.get_user_profile(u) is u


@pytest.mark.asyncio
async def test_get_user_profile_missing(user_service, mock_session):
    mock_session.execute.return_value = _scalar_result(None)
    with pytest.raises(HTTPException):
        await user_service.get_user_profile(_user(), target_user_id=uuid4())


@pytest.mark.asyncio
async def test_update_user_change_username(user_service, mock_session):
    u = _user()
    mock_session.execute.return_value = _scalar_result(u)
    data = UserUpdate(username="new")
    r = await user_service.update_user(u, data)
    assert r.username == "new"
    mock_session.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_update_user_no_fields_raises(user_service, mock_session):
    u = _user()
    mock_session.execute.return_value = _scalar_result(u)
    with pytest.raises(HTTPException):
        await user_service.update_user(u, UserUpdate())
    mock_session.commit.assert_not_awaited()


@pytest.mark.asyncio
async def test_delete_user_success(user_service, mock_session):
    u = _user()
    mock_session.execute.return_value = _scalar_result(u)
    await user_service.delete_user(u)
    mock_session.delete.assert_awaited_once_with(u)


@pytest.mark.asyncio
async def test_delete_user_missing(user_service, mock_session):
    mock_session.execute.return_value = _scalar_result(None)
    with pytest.raises(HTTPException):
        await user_service.delete_user(_user())


@pytest.mark.asyncio
async def test_send_otp_creates_entry(user_service, mock_session, monkeypatch):
    send = AsyncMock()
    monkeypatch.setattr("app.services.users.send_otp", send)
    await user_service.send_otp("+3")
    mock_session.add.assert_called()
    mock_session.commit.assert_awaited_once()
    send.assert_awaited_once()


@pytest.mark.asyncio
async def test_verify_otp_invalid_code(user_service, mock_session):
    otp = SimpleNamespace(
        id=uuid4(),
        phone_number="+5",
        code_hash=hashlib.sha256("000000".encode()).hexdigest(),
        expires_at=datetime.utcnow() + timedelta(minutes=1),
        used=False,
    )
    mock_session.execute.return_value = _scalar_result(otp)
    with pytest.raises(HTTPException):
        await user_service.verify_otp_and_create_user(otp.phone_number, "111111")


@pytest.mark.asyncio
async def test_verify_otp_expired(user_service, mock_session):
    otp = SimpleNamespace(
        id=uuid4(),
        phone_number="+6",
        code_hash=hashlib.sha256("000000".encode()).hexdigest(),
        expires_at=datetime.utcnow() - timedelta(minutes=1),
        used=False,
    )
    mock_session.execute.return_value = _scalar_result(otp)
    with pytest.raises(HTTPException):
        await user_service.verify_otp_and_create_user(otp.phone_number, "000000")
