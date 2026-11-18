from fastapi import Depends, FastAPI
from .core.config import Settings, get_settings

settings = get_settings()



app = FastAPI(title=settings.APP_NAME)


@app.get("/health")
async def health_check(settings: Settings = Depends(get_settings)) -> dict:
    return {"status": "ok", "app_name": settings.APP_NAME, "debug": settings.DEBUG, "port": settings.PORT}
