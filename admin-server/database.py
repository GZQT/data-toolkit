import datetime
from sqlalchemy import create_engine, DateTime, String
from sqlalchemy.orm import sessionmaker, DeclarativeBase, mapped_column, Mapped

POSTGRESQL_DATABASE_URL = f"postgresql://qtgc:QTgc2024@1.14.68.40:5432/qtgc_db"

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
