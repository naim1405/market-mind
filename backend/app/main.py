from fastapi import Depends, FastAPI
from sqlalchemy import text

from db.session import SessionDep

from .core.config import Settings, get_settings
from app.db.session import SessionDep

settings = get_settings()



app = FastAPI(title=settings.APP_NAME)


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
