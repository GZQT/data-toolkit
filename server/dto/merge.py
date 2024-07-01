from typing import List

from fastapi_camelcase import CamelModel


class MergeBase(CamelModel):
    file_path: str
    column: str


class MergeFiles(CamelModel):
    file_path: str
    select_columns: List[str]


class MergeRequest(CamelModel):
    base: MergeBase | None
    files: List[MergeFiles]
