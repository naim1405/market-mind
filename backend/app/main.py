from fastapi import Depends, FastAPI
from sqlalchemy import text

from app.api.v1.router import api_router
from app.core.config import Settings, get_settings
from app.core.exceptions.handlers import register_exception_handlers
from app.db.session import SessionDep

settings = get_settings()



app = FastAPI(title=settings.APP_NAME)
register_exception_handlers(app)
app.include_router(api_router)


@app.get("/health")
async def health_check(settings: Settings = Depends(get_settings)) -> dict:
    return {"status": "ok", "app_name": settings.APP_NAME, "debug": settings.DEBUG, "port": settings.PORT}

@app.get("/health/db")
async def health_check_db(session: SessionDep) -> dict:
    result = await session.execute(text("SELECT version();"))
    version= result.scalar()
    ext = await session.execute(text("SELECT extversion FROM pg_extension WHERE extname = 'vector'"))
    has_vector = ext.scalar_one_or_none() is not None
    return {"status": "ok", "db_version": version, "vector_extension":has_vector} 
