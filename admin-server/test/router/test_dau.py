import time

import pytest

from conf_test_db import override_get_db
from schema.dau import DauConfig


class TestDau:

    @pytest.fixture(autouse=True)
    def before(self, request):
        self.client = request.getfixturevalue('create_test_db')
        self.database = next(override_get_db())

    def test_create_dau(self):
        response = self.client.post('/dau', json={
            "name": "test_dau",
            "bridge": "test_dau",
            "collectionStationNo": "string",
            "collectionDeviceNo": "string",
            "ipAddress": "string",
            "sampleRate": "string",
            "physicsChannel": "string",
            "installNo": "string",
            "transferNo": "string",
            "monitorProject": "string",
            "deviceType": "string",
            "manufacturer": "string",
            "specification": "string",
            "deviceNo": "string",
            "installLocation": "string",
            "direction": "string"
        })
        assert response.status_code == 201
        content = self.database.query(DauConfig).filter_by(name="test_dau").all()
        assert len(content) == 1
        data = content[0]
        assert data.name == "test_dau"
        assert data.bridge == "test_dau"
        assert data.collection_station_no == "string"
        assert data.collection_device_no == "string"
        assert data.ip_address == "string"
        assert data.sample_rate == "string"
        assert data.physics_channel == "string"
        assert data.install_no == "string"
        assert data.transfer_no == "string"
        assert data.monitor_project == "string"
        assert data.device_type == "string"
        assert data.manufacturer == "string"
        assert data.device_no == "string"
        assert data.install_location == "string"
        assert data.direction == "string"

    def test_update_dau(self):
        response = self.client.post('/dau', json={
            "name": "need_update_dau",
            "bridge": "need_update_dau",
            "collectionStationNo": "string",
            "collectionDeviceNo": "string",
            "ipAddress": "string",
            "sampleRate": "string",
            "physicsChannel": "string",
            "installNo": "string",
            "transferNo": "string",
            "monitorProject": "string",
            "deviceType": "string",
            "manufacturer": "string",
            "specification": "string",
            "deviceNo": "string",
            "installLocation": "string",
            "direction": "string"
        })
        assert response.status_code == 201
        content = self.database.query(DauConfig).filter_by(name="need_update_dau").one()
        response = self.client.put(f'/dau/{content.id}', json={
            "name": "need_update_dau_1",
            "bridge": "need_update_dau_1",
            "collectionStationNo": "string_update",
            "collectionDeviceNo": "string_update",
            "ipAddress": "string_update",
            "sampleRate": "string_update",
            "physicsChannel": "string_update",
            "installNo": "string_update",
            "transferNo": "string_update",
            "monitorProject": "string_update",
            "deviceType": "string_update",
            "manufacturer": "string_update",
            "specification": "string_update",
            "deviceNo": "string_update",
            "installLocation": "string_update",
            "direction": "string_update"
        })
        assert response.status_code == 204
        content = self.database.query(DauConfig).filter_by(name="need_update_dau_1").all()
        assert len(content) == 1

    def test_delete_dau(self):
        response = self.client.post('/dau', json={
            "name": "need_det_dau",
            "bridge": "need_det_dau",
            "collectionStationNo": "string",
            "collectionDeviceNo": "string",
            "ipAddress": "string",
            "sampleRate": "string",
            "physicsChannel": "string",
            "installNo": "string",
            "transferNo": "string",
            "monitorProject": "string",
            "deviceType": "string",
            "manufacturer": "string",
            "specification": "string",
            "deviceNo": "string",
            "installLocation": "string",
            "direction": "string"
        })
        assert response.status_code == 201
        content = self.database.query(DauConfig).filter_by(name="need_det_dau").one()
        response = self.client.delete(f"/dau/{content.id}")
        assert response.status_code == 204
        content = self.database.query(DauConfig).filter_by(name="need_det_dau").all()
        assert len(content) == 0
