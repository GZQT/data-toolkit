import datetime
import os

from sqlalchemy import create_engine, DateTime, String
from sqlalchemy.orm import sessionmaker, DeclarativeBase, mapped_column, Mapped

POSTGRESQL_DATABASE_URL = os.getenv("DATABASE_URL")\
    if os.getenv("DATABASE_URL") else "postgresql://postgres:123456@192.168.68.225:5432/data_toolkit_dev"

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
