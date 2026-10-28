from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from src.config.base import db_settings

URL = (
    f"postgresql+asyncpg://"
    f"{db_settings.DB_USER}:"
    f"{db_settings.DB_PASSWORD}@"
    f"{db_settings.DB_HOST}:"
    f"{db_settings.DB_PORT}"
    f"/{db_settings.DB_NAME}"
)

async_engine = create_async_engine(url=URL, echo=True)
async_session = async_sessionmaker(bind=async_engine, expire_on_commit=False)