import datetime

from fastapi_camelcase import CamelModel


class DauResponse(CamelModel):
    id: int
    name: str
    collection_station_no: str | None
    collection_device_no: str | None
    ip_address: str | None
    sample_rate: str | None
    physics_channel: str | None
    install_no: str | None
    transfer_no: str | None
    monitor_project: str | None
    device_type: str | None
    manufacturer: str | None
    specification: str | None
    device_no: str | None
    install_location: str | None
    direction: str | None
    created_date: datetime.datetime
    updated_date: datetime.datetime
