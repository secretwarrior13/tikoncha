# app/api/endpoints/apps/router.py
import traceback
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user
from app.exc import LoggedHTTPException, raise_with_log  # your custom exceptions
from app.models.user import User
from app.schemas.apps import (
    AppBase,
    AppRequestCreate,
    AppRequestListItem,
    AppRequestResponse,
    AppResponse,
    InstalledAppResponse,
    TypesResponse,
    UninstallResponse,
)
from app.services.apps import AppService

router = APIRouter(
    prefix="/apps",
    tags=["Apps"],
)


@router.get("/", response_model=List[AppResponse], status_code=status.HTTP_200_OK)
async def read_apps(
    general_type: str | None = None,
    app_type: str | None = None,
    priority: str | None = None,
    session: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        return AppService(session).list_apps(
            current_user=current_user,
            general_type=general_type,
            app_type=app_type,
            priority=priority,
        )
    except LoggedHTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        traceback.print_exc()
        raise_with_log(
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            f"Failed to list apps: {e}",
        )


@router.get("/{app_id}", response_model=AppResponse, status_code=status.HTTP_200_OK)
async def read_app(
    app_id: int,
    session: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        app = AppService(session).get_app(current_user=current_user, app_id=app_id)
        if not app:
            raise HTTPException(status.HTTP_404_NOT_FOUND, detail="App not found")
        return app
    except LoggedHTTPException:
        raise
    except Exception as e:
        traceback.print_exc()
        raise_with_log(
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            f"Failed to get app {app_id}: {e}",
        )


@router.post(
    "/installed",
    response_model=InstalledAppResponse,
    status_code=status.HTTP_201_CREATED,
)
async def install_app(
    payload: AppBase,
    session: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        return AppService(session).register_installed_app(
            current_user=current_user,
            data=payload.model_dump(),
        )
    except LoggedHTTPException:
        raise
    except Exception as e:
        traceback.print_exc()
        raise_with_log(
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            f"Failed to register installed app: {e}",
        )


@router.post(
    "/request", response_model=AppRequestResponse, status_code=status.HTTP_201_CREATED
)
async def request_approval(
    payload: AppRequestCreate,
    session: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        return AppService(session).request_app_approval(
            current_user=current_user,
            data=payload.model_dump(),
        )
    except LoggedHTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        traceback.print_exc()
        raise_with_log(
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            f"Failed to request app approval: {e}",
        )


@router.get(
    "/requests", response_model=List[AppRequestListItem], status_code=status.HTTP_200_OK
)
async def read_requests(
    status_filter: str | None = None,
    session: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        return AppService(session).list_app_requests(
            current_user=current_user,
            status_filter=status_filter,
        )
    except LoggedHTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        traceback.print_exc()
        raise_with_log(
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            f"Failed to list app requests: {e}",
        )


@router.get("/types", response_model=TypesResponse, status_code=status.HTTP_200_OK)
async def read_types():
    # static, no session needed
    return AppService.get_types()


@router.post(
    "/{app_id}/uninstall",
    response_model=UninstallResponse,
    status_code=status.HTTP_200_OK,
)
async def uninstall_app(
    app_id: int,
    session: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        res = AppService(session).uninstall_app(
            current_user=current_user,
            app_id=app_id,
        )
        if not res:
            raise HTTPException(status.HTTP_404_NOT_FOUND, detail="App not installed")
        return res
    except LoggedHTTPException:
        raise
    except Exception as e:
        traceback.print_exc()
        raise_with_log(
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            f"Failed to uninstall app {app_id}: {e}",
        )
