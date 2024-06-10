import pytest
import sqlalchemy
from starlette.testclient import TestClient

from conf_test_db import app


@pytest.fixture(autouse=True)
def create_test_db():
    from conf_test_db import override_get_db
    database = next(override_get_db())
    result = database.execute(sqlalchemy.text("select version()"))
    version, = result.fetchone()
    print(f"PostgreSQL version {version}")

    client = TestClient(app)
    yield client
