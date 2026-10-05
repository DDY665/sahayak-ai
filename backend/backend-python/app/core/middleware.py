from __future__ import annotations

from time import perf_counter
from typing import Callable
from uuid import uuid4

from fastapi import Request

from app.core.logging_utils import emit_log


def create_request_id_middleware(logger):
    async def request_id_middleware(request: Request, call_next: Callable):
        request_id = request.headers.get("x-request-id") or str(uuid4())
        request.state.request_id = request_id
        started_at = perf_counter()

        logger.info(
            emit_log(
                "request.start",
                method=request.method,
                path=request.url.path,
                request_id=request_id,
            )
        )

        try:
            response = await call_next(request)
        except Exception:
            elapsed_ms = round((perf_counter() - started_at) * 1000)
            logger.exception(
                emit_log(
                    "request.error",
                    level="error",
                    method=request.method,
                    path=request.url.path,
                    request_id=request_id,
                    duration_ms=elapsed_ms,
                )
            )
            raise

        elapsed_ms = round((perf_counter() - started_at) * 1000)
        response.headers["x-request-id"] = request_id
        logger.info(
            emit_log(
                "request.end",
                method=request.method,
                path=request.url.path,
                status=response.status_code,
                request_id=request_id,
                duration_ms=elapsed_ms,
            )
        )
        return response

    return request_id_middleware
