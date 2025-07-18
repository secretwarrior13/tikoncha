import json
import logging

from fastapi import Request, HTTPException
from fastapi.routing import APIRoute
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError

logger = logging.getLogger(__name__)


class EnvelopeRoute(APIRoute):
    def get_route_handler(self):
        original_route_handler = super().get_route_handler()

        async def custom_route_handler(request: Request):
            try:
                response = await original_route_handler(request)

            except HTTPException as exc:
                response = JSONResponse(
                    {"detail": exc.detail}, status_code=exc.status_code
                )

            except IntegrityError as exc:
                logger.error(
                    "IntegrityError in %s %s",
                    request.method,
                    request.url,
                    exc_info=True,
                )
                response = JSONResponse(
                    {"detail": "Database conflict: " + str(exc.orig)}, status_code=409
                )

            except Exception as exc:
                logger.error(
                    "Unhandled error in %s %s",
                    request.method,
                    request.url,
                    exc_info=True,
                )
                response = JSONResponse(
                    {"detail": "Internal Server Error"}, status_code=500
                )

            if response.media_type == "application/json":
                try:
                    body = json.loads(response.body)
                except Exception:
                    body = response.body.decode(errors="ignore")

                envelope = {
                    "status_code": response.status_code,
                    "data": body,
                }
                return JSONResponse(envelope, status_code=200)

            return response

        return custom_route_handler
