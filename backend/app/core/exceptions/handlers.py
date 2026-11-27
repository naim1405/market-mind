from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.core.exceptions.errors import BadRequestError, ConflictError, NotFoundError


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(exc_class_or_status_code=NotFoundError)
    async def not_found(_: Request, exc: NotFoundError) -> JSONResponse:
        return JSONResponse(status_code=404, content={"detail": str(exc)})

    @app.exception_handler(exc_class_or_status_code=ConflictError)
    async def conflict(_: Request, exc: ConflictError) -> JSONResponse:
        return JSONResponse(status_code=409, content={"detail": str(exc)})

    @app.exception_handler(exc_class_or_status_code=BadRequestError)
    async def bad_request(_: Request, exc: BadRequestError) -> JSONResponse:
        return JSONResponse(status_code=400, content={"detail": str(exc)})
