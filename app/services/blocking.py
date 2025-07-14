# app/api/endpoints/blocking/service.py
from datetime import datetime
from typing import Any, Dict, List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.enums.enums import AppRequestStatuses
from app.models.device import UserApp
from app.models.user import App, School, StudentInfo, User, UserType


class BlockingServiceAsync:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def _ensure_student(self, user: User) -> StudentInfo:
        ut = await self.db.get(UserType, user.user_type_id)
        if not ut or ut.name != "student":
            raise PermissionError("Only students may access blocking data")

        result = await self.db.execute(select(StudentInfo).filter_by(user_id=user.id))
        si = result.scalars().first()
        if not si:
            raise LookupError("Student profile not found")
        return si

    async def get_status(self, user: User) -> Dict[str, Any]:
        si = await self._ensure_student(user)

        school_name = "Unknown"
        if si.school:
            sch = await self.db.get(School, si.school)
            if sch:
                school_name = sch.name

        now = datetime.now()
        return {
            "blocking_active": True,
            "reason": "School hours (8:00 AM - 2:00 PM)",
            "location_based": True,
            "school_detected": school_name,
            "current_time": now.strftime("%H:%M"),
            "is_holiday": False,
            "shift": si.shift.value if si.shift else None,
        }

    async def list_blocked_apps(self, user: User) -> List[Dict[str, Any]]:
        await self._ensure_student(user)

        result = await self.db.execute(select(App).limit(10))
        apps = result.scalars().all()

        out: List[Dict[str, Any]] = []
        for a in apps:
            ua_res = await self.db.execute(
                select(UserApp).filter_by(user_id=user.id, app_id=a.id)
            )
            installed = ua_res.scalars().first() is not None

            is_blocked = a.general_type and a.general_type.value == "Social"

            out.append(
                {
                    "id": a.id,
                    "package_name": a.package_name,
                    "app_name": a.name,
                    "is_blocked": is_blocked,
                    "installed": installed,
                    "category": a.general_type.value if a.general_type else "Unknown",
                }
            )

        return out

    async def request_exception(
        self, user: User, app_id: int, reason: str
    ) -> Dict[str, Any]:
        await self._ensure_student(user)

        a = await self.db.get(App, app_id)
        if not a:
            raise LookupError("App not found")

        return {
            "message": "Emergency exception request submitted successfully",
            "status": AppRequestStatuses.pending.value,
            "estimated_review_time": "within 30 minutes",
            "app_id": app_id,
            "app_name": a.name,
            "reason": reason,
        }

    async def get_schedule(
        self, user: User, month: Optional[int], year: Optional[int]
    ) -> Dict[str, Any]:
        si = await self._ensure_student(user)

        now = datetime.now()
        m = month or now.month
        y = year or now.year

        holidays = [
            {"date": f"{y}-{m:02d}-21", "name": "Navruz Holiday"},
            {"date": f"{y}-{m:02d}-30", "name": "Teacher Development Day"},
        ]
        specials = [
            {
                "date": f"{y}-{m:02d}-15",
                "name": "Science Fair",
                "blocking_modified": True,
            }
        ]

        return {
            "month": m,
            "year": y,
            "school_id": si.school,
            "shift": si.shift.value if si.shift else None,
            "holidays": holidays,
            "special_events": specials,
        }
