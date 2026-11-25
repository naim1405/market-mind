# handle http
from fastapi import APIRouter
from fastapi.responses import RedirectResponse

from app.modules.auth.dependencies import AuthServiceDep

router = APIRouter(prefix="/auth", tags=["auth"])



@router.get("/")
async def auth_root(service:AuthServiceDep):
    return service.hello_auth()


@router.get("/facebook")
async def login_by_facebook(service:AuthServiceDep):
    redirect_url = service.login_by_facebook()
    return RedirectResponse(url=redirect_url)


@router.get("/facebook/callback")
async def facebook_callback(
    code: str,
    service: AuthServiceDep,
    error: str | None = None,
):
    if error:
        return {"error": error}
    if not code:
        return {"error": "No code provided"}
    return await service.handle_facebook_callback(code)
