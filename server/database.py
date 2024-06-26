import datetime

from sqlalchemy import create_engine, DateTime, String, NullPool
from sqlalchemy.orm import sessionmaker, DeclarativeBase, mapped_column, Mapped

from constant import ROOT_DIRECTORY

SQLALCHEMY_DATABASE_URL = f"sqlite:///{ROOT_DIRECTORY}/sql_app.db"

# https://docs.sqlalchemy.org/en/20/core/pooling.html#using-connection-pools-with-multiprocessing-or-os-fork
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False},
    poolclass=NullPool
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


class CommonSchema(Base):
    __abstract__ = True

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(1024))
    created_date: Mapped[datetime] = mapped_column(DateTime(), default=datetime.datetime.now)
    updated_date: Mapped[datetime] = mapped_column(DateTime(), default=datetime.datetime.now)
