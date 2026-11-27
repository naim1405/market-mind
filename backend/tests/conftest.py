import os

# must be set before the app (and its settings/engine) are imported
os.environ["DB_NAME"] = "market_mind_ai_test"

import asyncpg
import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

import app.db.all_models  # noqa: F401  registers every table on Base.metadata
from app.core.config import get_settings
from app.db.base import Base
from app.db.session import get_session
from app.main import app
from app.modules.pages.models import Pages
from app.modules.users.models import User

settings = get_settings()


@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"


async def _create_test_database():
    conn = await asyncpg.connect(
        host=settings.DB_HOST,
        port=int(settings.DB_PORT),
        user=settings.DB_USER,
        password=settings.DB_PASSWORD.get_secret_value(),
        database="postgres",
    )
    try:
        exists = await conn.fetchval(
            "SELECT 1 FROM pg_database WHERE datname = $1", settings.DB_NAME
        )
        if not exists:
            await conn.execute(f'CREATE DATABASE "{settings.DB_NAME}"')
    finally:
        await conn.close()


@pytest.fixture(scope="session")
async def engine():
    await _create_test_database()
    engine = create_async_engine(settings.DATABASE_URL)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    await engine.dispose()


@pytest.fixture
async def db_session(engine):
    # everything a test does, including the app's commits, is rolled back at the end
    async with engine.connect() as conn:
        trans = await conn.begin()
        session = AsyncSession(
            bind=conn, expire_on_commit=False, join_transaction_mode="create_savepoint"
        )
        yield session
        await session.close()
        await trans.rollback()


@pytest.fixture
async def client(db_session):
    async def override_get_session():
        yield db_session

    app.dependency_overrides[get_session] = override_get_session
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture
async def page(db_session):
    user = User(email="owner@example.com", name="Owner", facebook_id="fb-user-1")
    db_session.add(user)
    await db_session.flush()
    page = Pages(
        facebook_id="fb-page-1", name="Test Shop", access_token="token", user_id=user.id
    )
    db_session.add(page)
    await db_session.flush()
    return page


@pytest.fixture
async def product(db_session, page):
    from app.modules.products.models import Product

    product = Product(
        page_id=page.id,
        sku="PJ-01",
        name="Cotton Panjabi",
        category="Panjabi",
        selling_price=1500,
        min_floor_price=1200,
        stock_qty=5,
        image_urls=["https://res.cloudinary.com/demo/a.jpg"],
    )
    db_session.add(product)
    await db_session.flush()
    return product


@pytest.fixture
async def customer(db_session, page):
    from app.modules.customers.models import Customer

    customer = Customer(page_id=page.id, psid="psid-1", name="Rahim")
    db_session.add(customer)
    await db_session.flush()
    return customer
