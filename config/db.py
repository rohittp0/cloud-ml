from typing import Generator

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker, Session, as_declarative, declared_attr

from config.variables import set_up

config = set_up()


class AsyncDatabaseSession:
    def __init__(self):
        self._session = None
        self._engine = None

    def __getattr__(self, name):
        return getattr(self._session, name)

    def init(self):
        db = config["database"]
        db_url = f"postgresql+asyncpg://{db['user']}:{db['password']}@localhost/{db['name']}"
        self._engine = create_async_engine(db_url, future=False)
        self._session = sessionmaker(self._engine, expire_on_commit=False, class_=AsyncSession)()


async def create_all(self):
    async with self._engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def get_db() -> Generator[Session, None, None]:
    db = AsyncDatabaseSession()
    db.init()

    try:
        yield db
    finally:
        await db.close()


@as_declarative(class_registry=dict())
class Base:
    id: int
    __name__: str

    @declared_attr
    def __tablename__(self) -> str:
        return self.__name__.lower()
