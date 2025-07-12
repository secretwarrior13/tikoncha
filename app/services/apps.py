# app/api/endpoints/apps/service.py
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session

from app.models.user import App
from app.models.device import UserApp
from app.models.app_request import AppRequest
from app.models.user import User
from app.enums.enums import (
    GeneralType,
    AppType,
    Priorities,
    AppRequestStatuses,
)


class AppService:
    def __init__(self, session: Session):
        self.session = session

    def list_apps(
        self,
        current_user: User,
        general_type: Optional[str],
        app_type: Optional[str],
        priority: Optional[str],
    ) -> List[Dict[str, Any]]:
        q = self.session.query(App)

        if general_type:
            try:
                gt = GeneralType(general_type)
            except ValueError:
                raise ValueError(f"Invalid general_type: {general_type}")
            q = q.filter(App.general_type == gt)

        if app_type:
            try:
                at = AppType(app_type)
            except ValueError:
                raise ValueError(f"Invalid app_type: {app_type}")
            q = q.filter(App.app_type == at)

        if priority:
            try:
                pr = Priorities(priority)
            except ValueError:
                raise ValueError(f"Invalid priority: {priority}")
            q = q.filter(App.priority == pr)

        apps = q.all()
        result: List[Dict[str, Any]] = []

        for app in apps:
            installed = (
                self.session.query(UserApp)
                .filter_by(user_id=current_user.id, app_id=app.id)
                .first()
                is not None
            )
            result.append(
                {
                    "id": app.id,
                    "name": app.name,
                    "package_name": app.package_name,
                    "general_type": (
                        app.general_type.value if app.general_type else None
                    ),
                    "app_type": app.app_type.value if app.app_type else None,
                    "priority": app.priority.value if app.priority else None,
                    "installed": installed,
                    "created_at": app.created_at,
                    "updated_at": app.updated_at,
                }
            )

        return result

    def get_app(
        self,
        current_user: User,
        app_id: int,
    ) -> Dict[str, Any]:
        app = self.session.get(App, app_id)
        if not app:
            return None

        installed = (
            self.session.query(UserApp)
            .filter_by(user_id=current_user.id, app_id=app.id)
            .first()
            is not None
        )
        return {
            "id": app.id,
            "name": app.name,
            "package_name": app.package_name,
            "general_type": app.general_type.value if app.general_type else None,
            "app_type": app.app_type.value if app.app_type else None,
            "priority": app.priority.value if app.priority else None,
            "installed": installed,
            "created_at": app.created_at,
            "updated_at": app.updated_at,
        }

    def register_installed_app(
        self,
        current_user: User,
        data: Dict[str, Any],
    ) -> Dict[str, Any]:
        try:
            # lookup or create App
            app = (
                self.session.query(App)
                .filter_by(package_name=data["package_name"])
                .first()
            )
            if not app:
                app = App(
                    name=data["name"],
                    package_name=data["package_name"],
                    general_type=data.get("general_type"),
                    app_type=data.get("app_type"),
                    priority=data.get("priority"),
                )
                self.session.add(app)
                self.session.flush()

            # lookup or update UserApp
            ua = (
                self.session.query(UserApp)
                .filter_by(user_id=current_user.id, app_id=app.id)
                .first()
            )
            if ua:
                ua.is_active = True
                self.session.commit()
                return {
                    "message": "App installation updated",
                    "app_id": app.id,
                    "user_app_id": ua.id,
                }

            ua = UserApp(user_id=current_user.id, app_id=app.id, is_active=True)
            self.session.add(ua)
            self.session.commit()
            self.session.refresh(ua)

            return {
                "message": "App installation registered successfully",
                "app_id": app.id,
                "user_app_id": ua.id,
            }

        except Exception:
            self.session.rollback()
            raise

    def request_app_approval(
        self,
        current_user: User,
        data: Dict[str, Any],
    ) -> Dict[str, Any]:
        app = self.session.get(App, data["app_id"])
        if not app:
            raise ValueError("App not found")

        existing = (
            self.session.query(AppRequest)
            .filter_by(
                user_id=current_user.id,
                app_id=data["app_id"],
                status=AppRequestStatuses.pending,
            )
            .first()
        )
        if existing:
            raise ValueError("A pending request already exists")

        ar = AppRequest(
            user_id=current_user.id,
            app_id=data["app_id"],
            reason=data["reason"],
            status=AppRequestStatuses.pending,
        )
        self.session.add(ar)
        self.session.commit()
        self.session.refresh(ar)

        return {
            "message": "App approval request submitted successfully",
            "request_id": ar.id,
            "app_id": ar.app_id,
            "app_name": app.name,
            "status": ar.status.value,
            "created_at": ar.created_at,
        }

    def list_app_requests(
        self,
        current_user: User,
        status_filter: Optional[str],
    ) -> List[Dict[str, Any]]:
        q = self.session.query(AppRequest).filter_by(user_id=current_user.id)
        if status_filter:
            try:
                sf = AppRequestStatuses(status_filter)
            except ValueError:
                raise ValueError(f"Invalid status: {status_filter}")
            q = q.filter(AppRequest.status == sf)

        out: List[Dict[str, Any]] = []
        for r in q.all():
            app = self.session.get(App, r.app_id)
            out.append(
                {
                    "id": r.id,
                    "app_id": r.app_id,
                    "app_name": app.name if app else "Unknown",
                    "reason": r.reason,
                    "status": r.status.value,
                    "created_at": r.created_at,
                    "updated_at": r.updated_at,
                }
            )
        return out

    @staticmethod
    def get_types() -> Dict[str, Dict[str, str]]:
        return {
            "general_types": {g.name: g.value for g in GeneralType},
            "app_types": {a.name: a.value for a in AppType},
            "priorities": {p.name: p.value for p in Priorities},
        }

    def uninstall_app(
        self,
        current_user: User,
        app_id: int,
    ) -> Dict[str, Any]:
        ua = (
            self.session.query(UserApp)
            .filter_by(user_id=current_user.id, app_id=app_id)
            .first()
        )
        if not ua:
            return None

        ua.is_active = False
        self.session.commit()
        return {
            "message": "App marked as uninstalled",
            "app_id": app_id,
        }
