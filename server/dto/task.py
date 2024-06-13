import datetime

from fastapi_camelcase import CamelModel
from pydantic import ConfigDict


class TaskBase(CamelModel):
    name: str


class TaskResponse(TaskBase):
    id: int
    created_date: datetime.datetime
    updated_date: datetime.datetime

    model_config = ConfigDict(from_attributes=True)


class TaskCreateRequest(TaskBase):
    pass


class TaskFileCreateRequest(CamelModel):
    names: list[str]


class TaskFileUpdateRequest(TaskBase):
    pass


class TaskFileResponse(TaskBase):
    id: int
    task_id: int
    created_date: datetime.datetime
    updated_date: datetime.datetime

    model_config = ConfigDict(from_attributes=True)
