from typing import List

from fastapi_camelcase import CamelModel


class MergeBase(CamelModel):
    file_path: str
    column: str


class MergeFiles(CamelModel):
    file_path: str
    select_columns: List[str]

class MergeConfig(CamelModel):
    remove_base_null: bool = True
    remove_null: bool = False

class MergeRequest(CamelModel):
    base: MergeBase | None
    files: List[MergeFiles]
    config: MergeConfig | None
