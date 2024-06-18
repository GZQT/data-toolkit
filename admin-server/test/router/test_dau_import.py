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
        self.file = ('test_import_DAU配置表.xls',
                     open(os.path.join(current_file_path, 'test_import_DAU配置表.xls'), 'rb'),
                     'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')

    def test_import_dau(self):
        response = self.client.post("/dau/import", files={
            "files": self.file
        })
        assert response.status_code == 201
        data = self.database.query(DauConfig).filter_by(name='test_import_').all()
        assert len(data) == 104

    def test_import_exist_bridge(self):
        self.file = ('1——test_import_DAU配置表.xls',
                     open(os.path.join(current_file_path, 'test_import_DAU配置表.xls'), 'rb'),
                     'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response = self.client.post("/dau/import", files={
            "files": self.file
        })
        assert response.status_code == 201
        response = self.client.post("/dau/import", files={
            "files": self.file
        })
        assert response.status_code == 201
        data = self.database.query(DauConfig).filter_by(name='1——test_import_').all()
        assert len(data) == 104

    def test_import_no_excel(self):
        response = self.client.post("/dau/import", files={
            "files": ('__init__.py', open('__init__.py', 'rb'))
        })
        assert response.status_code == 201

    def test_import_no_files(self):
        response = self.client.post("/dau/import", files={
            "files": {}
        })
        assert response.status_code == 400
