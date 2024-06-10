import string

from sqlalchemy import ForeignKey, String, Enum, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database import CommonSchema


class DauConfig(CommonSchema):
    __tablename__ = "dau_config"

    bridge: Mapped[string] = mapped_column(String(128), nullable=False, comment="桥梁名称")
    collection_station_no: Mapped[string] = mapped_column(String(128), nullable=True, comment="采集站编号")
    collection_device_no: Mapped[string] = mapped_column(String(128), nullable=True, comment="采集设备编号")
    ip_address: Mapped[string] = mapped_column(String(128), nullable=True, comment="IP地址")
    sample_rate: Mapped[string] = mapped_column(String(128), nullable=True, comment="采样率")
    physics_channel: Mapped[string] = mapped_column(String(128), nullable=True, comment="物理通道")
    install_no: Mapped[string] = mapped_column(String(128), nullable=True, comment="安装点编号")
    transfer_no: Mapped[string] = mapped_column(String(128), nullable=True, comment="传输编号")
    monitor_project: Mapped[string] = mapped_column(String(128), nullable=True, comment="监测项目")
    device_type: Mapped[string] = mapped_column(String(128), nullable=True, comment="设备类型")
    manufacturer: Mapped[string] = mapped_column(String(128), nullable=True, comment="厂家名称")
    specification: Mapped[string] = mapped_column(String(128), nullable=True, comment="规格型号")
    device_no: Mapped[string] = mapped_column(String(128), nullable=True, comment="设备编号")
    install_location: Mapped[string] = mapped_column(String(128), nullable=True, comment="安装位置")
    direction: Mapped[string] = mapped_column(String(128), nullable=True, comment="方向")
