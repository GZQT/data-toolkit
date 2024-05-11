import pytest


class TestTaskFile:

    @pytest.fixture(autouse=True)
    def setup_class(self, request):
        self.client = request.getfixturevalue('create_test_db')
        response = self.client.get("/task")
        assert response.status_code == 200
        task_list = response.json()
        assert len(task_list) > 0
        self.task = task_list[0]
        response = self.client.post(f"/task/{self.task['id']}/file", json={"names": ["test_task_file_new"]})
        assert response.status_code == 201

    def test_add_task_file(self):
        response = self.client.post(f"/task/{self.task['id']}/file", json={"names": ["test_task_file_new"]})
        assert response.status_code == 201

    def test_get_task_file(self):
        response = self.client.get(f"/task/{self.task['id']}/file")
        assert response.status_code == 200
        assert len(response.json()) > 0

    def test_add_task_file_not_task(self):
        response = self.client.post(f"/task/199999999/file", json={"names": ["test_task_file_new"]})
        assert response.status_code == 400
        assert response.json()['detail'] == '关联的任务不存在，请重新选择任务后进行创建'
