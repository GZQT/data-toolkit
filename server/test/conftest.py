import pytest
from starlette.testclient import TestClient

from schema.task import Task
from conf_test_db import app


@pytest.fixture(autouse=True)
def create_test_db():
    from conf_test_db import override_get_db
    database = next(override_get_db())

    task = Task(name="test_task")
    database.add(task)
    database.commit()

    client = TestClient(app)
    yield client
