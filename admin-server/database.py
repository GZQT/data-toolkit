import datetime
import os

from sqlalchemy import create_engine, DateTime, String
from sqlalchemy.orm import sessionmaker, DeclarativeBase, mapped_column, Mapped

from config import env_config

POSTGRESQL_DATABASE_URL = env_config["DATABASE_URL"]\
    if env_config["DATABASE_URL"] is not None else "postgresql://postgres:123456@192.168.68.225:5432/data_toolkit_dev"

print("POSTGRESQL_DATABASE_URL", POSTGRESQL_DATABASE_URL)
engine = create_engine(POSTGRESQL_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


class CommonSchema(Base):
    __abstract__ = True

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(1024))
    created_date: Mapped[datetime] = mapped_column(DateTime(), default=datetime.datetime.now())
    updated_date: Mapped[datetime] = mapped_column(DateTime(), default=datetime.datetime.now())
