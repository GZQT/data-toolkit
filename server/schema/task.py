import json
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
    config: Mapped[str] = mapped_column(String(2048), nullable=True)

    task_id: Mapped[int] = mapped_column(ForeignKey("task.id"))
    task: Mapped["Task"] = relationship(back_populates="generators")

    @property
    def file_list(self):
        if self.files is None:
            return []
        return self.files.split("_:_")

    @property
    def config_obj(self):
        if self.config is None:
            return None
        return json.loads(self.config)
