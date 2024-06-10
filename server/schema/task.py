import string
from typing import List

from sqlalchemy import ForeignKey, String, Enum, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database import CommonSchema
from dto.generator import GeneratorResultEnum


class Task(CommonSchema):
    __tablename__ = "task"

    files: Mapped[List["TaskFile"]] = relationship(back_populates="task", cascade="all, delete")
    generators: Mapped[List["TaskGenerator"]] = relationship(back_populates="task", cascade="all, delete")


class TaskFile(CommonSchema):
    __tablename__ = "task_file"

    task_id: Mapped[int] = mapped_column(ForeignKey("task.id"))
    task: Mapped["Task"] = relationship(back_populates="files")


class TaskGenerator(CommonSchema):
    __tablename__ = "generator"

    # sqlite 中不允许使用 array 字段类型，所以这里以 _:_ 进行分割文件路径
    files: Mapped[string] = mapped_column(String(2048), nullable=True)
    status: Mapped[Enum[string]] = mapped_column(
        Enum(GeneratorResultEnum, name='GeneratorResult'), default="WAITING")
    output: Mapped[str] = mapped_column(Text, nullable=True)
    result: Mapped[string] = mapped_column(String(2048), nullable=True)

    task_id: Mapped[int] = mapped_column(ForeignKey("task.id"))
    task: Mapped["Task"] = relationship(back_populates="generators")
    dau_config_id: Mapped[int] = mapped_column(ForeignKey("dau_config.id", name="generator_dau_config"), nullable=True)
    dau_config: Mapped["DauConfig"] = relationship(back_populates="generators")

    @property
    def file_list(self):
        if self.files is None:
            return []
        return self.files.split("_:_")


class DauConfig(CommonSchema):
    __tablename__ = "dau_config"

    bridge: Mapped[string] = mapped_column(String(128), nullable=False)
    collection_station_no: Mapped[string] = mapped_column(String(128), nullable=True)
    collection_device_no: Mapped[string] = mapped_column(String(128), nullable=True)
    ip_address: Mapped[string] = mapped_column(String(128), nullable=True)
    sample_rate: Mapped[string] = mapped_column(String(128), nullable=True)
    physics_channel: Mapped[string] = mapped_column(String(128), nullable=True)
    install_no: Mapped[string] = mapped_column(String(128), nullable=True)
    transfer_no: Mapped[string] = mapped_column(String(128), nullable=True)
    monitor_project: Mapped[string] = mapped_column(String(128), nullable=True)
    device_type: Mapped[string] = mapped_column(String(128), nullable=True)
    manufacturer: Mapped[string] = mapped_column(String(128), nullable=True)
    specification: Mapped[string] = mapped_column(String(128), nullable=True)
    device_no: Mapped[string] = mapped_column(String(128), nullable=True)
    install_location: Mapped[string] = mapped_column(String(128), nullable=True)
    direction: Mapped[string] = mapped_column(String(128), nullable=True)

    generators: Mapped[List["TaskGenerator"]] = \
        relationship(back_populates="dau_config", cascade="all, delete")
