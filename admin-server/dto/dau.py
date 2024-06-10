import datetime

from fastapi_camelcase import CamelModel
from schema.dau import DauConfig


class DauSearchRequest(CamelModel):
    name: str | None = None
    bridge: str | None = None
    collection_station_no: str | None = None
    collection_device_no: str | None = None
    ip_address: str | None = None
    sample_rate: str | None = None
    physics_channel: str | None = None
    install_no: str | None = None
    transfer_no: str | None = None
    monitor_project: str | None = None
    device_type: str | None = None
    manufacturer: str | None = None
    specification: str | None = None
    device_no: str | None = None
    install_location: str | None = None
    direction: str | None = None

    def to_orm(self):
        return DauConfig(
            name=self.name,
            bridge=self.bridge,
            collection_station_no=self.collection_station_no,
            collection_device_no=self.collection_device_no,
            ip_address=self.ip_address,
            sample_rate=self.sample_rate,
            physics_channel=self.physics_channel,
            install_no=self.install_no,
            transfer_no=self.transfer_no,
            monitor_project=self.monitor_project,
            device_type=self.device_type,
            manufacturer=self.manufacturer,
            specification=self.specification,
            device_no=self.device_no,
            install_location=self.install_location,
            direction=self.direction,
            updated_date=datetime.datetime.now()
        )


class DauSearchResponse(DauSearchRequest):
    id: int | None
    created_date: datetime.datetime | None
    updated_date: datetime.datetime | None
