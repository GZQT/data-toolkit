from testcontainers.postgres import PostgresContainer

from application import app
from database import Base
from dependency import get_db
from sqlalchemy import create_engine, StaticPool
from sqlalchemy.orm import sessionmaker

container = PostgresContainer()
container.start()
engine = create_engine(
    container.get_connection_url(),
    poolclass=StaticPool,
)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base.metadata.create_all(bind=engine)


def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db
