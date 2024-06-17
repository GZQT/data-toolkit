import os

import pytest

from conf_test_db import override_get_db
from schema.dau import DauConfig

current_file_path = os.path.dirname(os.path.abspath(__file__))


class TestDauImport:

    @pytest.fixture(autouse=True)
    def setup_class(self, request):
        self.client = request.getfixturevalue('create_test_db')
        self.database = next(override_get_db())
        self.file = ('test_import_dau_file.xls',
                     open(os.path.join(current_file_path, 'test_import_dau_file.xls'), 'rb'),
                     'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')

    def test_import_dau(self):
        response = self.client.post("/dau/import/test_bridge_import", files={
            "files": self.file
        })
        assert response.status_code == 201
        data = self.database.query(DauConfig).filter_by(name='test_bridge_import').all()
        assert len(data) == 52

    def test_import_exist_bridge(self):
        response = self.client.post("/dau/import/test_bridge_exist", files={
            "files": self.file
        })
        assert response.status_code == 201
        response = self.client.post("/dau/import/test_bridge_exist", files={
            "files": self.file
        })
        assert response.status_code == 400
        body = response.json()
        assert body['detail'] == '已经存在当前桥梁的数据了，无需再进行添加'

    def test_import_no_excel(self):
        response = self.client.post("/dau/import/test_bridge_no_excel", files={
            "files": ('__init__.py', open('__init__.py', 'rb'))
        })
        assert response.status_code == 400
        body = response.json()
        assert body['detail'] == '文件 __init__.py 并不是一个 Excel 文件'

    def test_import_no_files(self):
        response = self.client.post("/dau/import/test_bridge_exist", files={
            "files": {}
        })
        assert response.status_code == 400
