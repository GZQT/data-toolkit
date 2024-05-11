import uuid


class TestTask:

    def test_add_task(self, request):
        client = request.getfixturevalue('create_test_db')
        name = f"{uuid.uuid4()}"
        response = client.post("/task", json={
            "name": name
        })
        assert response.status_code == 200
        body = response.json()
        assert body['name'] == name
        assert body['id'] > 0

    def test_get_task(self, request):
        client = request.getfixturevalue('create_test_db')
        response = client.get("/task")
        assert response.status_code == 200
        body = response.json()
        assert len(body) > 0
