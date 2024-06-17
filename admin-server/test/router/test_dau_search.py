import math
import os

import pytest

from conf_test_db import override_get_db
from schema.dau import DauConfig


def _assert_page(response, items, total, page, size):
    assert response.status_code == 200
    body = response.json()
    assert len(body["items"]) == items
    assert body["total"] == total
    assert body["page"] == page
    assert body["size"] == size
    assert body["pages"] == math.ceil(total / size)
    return body


current_file_path = os.path.dirname(os.path.abspath(__file__))


class TestDauSearch:

    @pytest.fixture(autouse=True)
    def before(self, request):
        self.client = request.getfixturevalue('create_test_db')
        self.database = next(override_get_db())
        self.client.post("/dau/import/test_dau_search", files={
            "files": ('test_import_dau_file.xls',
                      open(os.path.join(current_file_path, 'test_import_dau_file.xls'), 'rb'),
                      'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        })
        data = self.database.query(DauConfig).all()
        assert len(data) >= 52

    def test_search_name(self):
        response = self.client.get("/dau", params={"page": 1, "size": 20, "name": "test_bridge_no_data_1"})
        _assert_page(response, 0, 0, 1, 20)

    def test_search_other_conditions(self):
        response = self.client.get("/dau", params={
            "name": "test_dau_search", "collectionStationNo": "DAU1"
        })
        _assert_page(response, 50, 52, 1, 50)
        response = self.client.get("/dau", params={
            "name": "test_dau_search", "collectionDeviceNo": "AAA(A)-AAA-03"
        })
        _assert_page(response, 5, 5, 1, 50)
        response = self.client.get("/dau", params={
            "name": "test_dau_search", "ipAddress": "1.1.1.1"
        })
        _assert_page(response, 7, 7, 1, 50)
        response = self.client.get("/dau", params={"name": "test_dau_search", "sampleRate": "1HZ"})
        _assert_page(response, 23, 23, 1, 50)
        response = self.client.get("/dau", params={
            "name": "test_dau_search", "collectionDeviceNo": "AAA(A)-AAA-03", "physicsChannel": "1"
        })
        _assert_page(response, 1, 1, 1, 50)
        response = self.client.get("/dau", params={
            "name": "test_dau_search", "ipAddress": "1.1.1.1", "installNo": "TT-TTT-TT-A-01"
        })
        _assert_page(response, 1, 1, 1, 50)
        response = self.client.get("/dau", params={
            "name": "test_dau_search", "ipAddress": "1.1.1.1", "transferNo": "5200090025"
        })
        _assert_page(response, 1, 1, 1, 50)
        response = self.client.get("/dau", params={
            "name": "test_dau_search", "ipAddress": "1.1.1.1", "monitorProject": "项目1"
        })
        _assert_page(response, 7, 7, 1, 50)
        response = self.client.get("/dau", params={
            "name": "test_dau_search", "ipAddress": "1.1.1.1", "deviceType": "类型1"
        })
        _assert_page(response, 7, 7, 1, 50)
        response = self.client.get("/dau", params={
            "name": "test_dau_search", "ipAddress": "1.1.1.1", "manufacturer": "小厂"
        })
        _assert_page(response, 7, 7, 1, 50)
        response = self.client.get("/dau", params={
            "name": "test_dau_search", "ipAddress": "1.1.1.1", "specification": "AAAA-AA-A-01"
        })
        _assert_page(response, 1, 1, 1, 50)
        response = self.client.get("/dau", params={
            "name": "test_dau_search", "ipAddress": "1.1.1.1", "deviceNo": "BBBBBB-12-1"
        })
        _assert_page(response, 1, 1, 1, 50)
        response = self.client.get("/dau", params={
            "name": "test_dau_search", "ipAddress": "1.1.1.1", "installLocation": "位置1"
        })
        _assert_page(response, 1, 1, 1, 50)
        response = self.client.get("/dau", params={
            "name": "test_dau_search", "ipAddress": "1.1.1.1", "direction": "竖向"
        })
        _assert_page(response, 7, 7, 1, 50)
