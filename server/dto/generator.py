import datetime
from enum import Enum
from typing import List

from fastapi_camelcase import CamelModel


class GeneratorResultEnum(str, Enum):
    SUCCESS = 'SUCCESS'
    PROCESSING = 'PROCESSING'
    FAILED = 'FAILED'
    WAITING = 'WAITING'


class ChartFillEnum(Enum):
    # 向前填充
    FORWARD_FILL = 'FORWARD_FILL'
    # 后向填充
    BACKWARD_FILL = 'BACKWARD_FILL'
    NONE = 'NONE'
    LINE = 'LINE'
    # 时间插值
    TIME = 'TIME'


class GeneratorBase(CamelModel):
    name: str


class GeneratorResponse(GeneratorBase):
    id: int
    created_date: datetime.datetime
    updated_date: datetime.datetime
    files: str | None
    status: GeneratorResultEnum = GeneratorResultEnum.PROCESSING
    result: str | None


class GeneratorAllResponse(GeneratorResponse):
    output: str | None


class GeneratorCreateRequest(GeneratorBase):
    files: str


class TaskGeneratorStartRequest(CamelModel):
    average_line_chart: bool
    average_line_chart_column_index: List[int] = []
    average_line_chart_time_range: str = '10T'
    average_line_chart_x_label: str
    average_line_chart_y_label: str
    average_line_chart_x_rotation: float
    average_line_chart_name: List[str]
    average_line_chart_fill: ChartFillEnum | None = None
    average_line_chart_line_width: float = 1
    average_line_chart_show_grid: bool = True

    max_min_line_chart: bool
    max_min_line_chart_column_index: List[int] = []
    max_min_line_chart_time_range: str = '10T'
    max_min_line_chart_x_label: str
    max_min_line_chart_y_label: str
    max_min_line_chart_x_rotation: float
    max_min_line_chart_name: List[str]
    max_min_line_chart_fill: ChartFillEnum | None = None
    max_min_line_chart_line_width: float = 1
    max_min_line_chart_show_grid: bool = True

    average_bar_chart: bool
    max_min_bar_chart: bool
    average_data_table: bool
    max_min_data_table: bool
    average_bar_group: List[List[int]]
    max_min_bar_group: List[List[int]]


class BarChartGeneratorStartRequest(CamelModel):
    generator_ids: List[int]
    chart_name: str | None
    # 时间紧迫，最快捷的方阿了这是
    compare_group: List[List[List[int]]]
    x_label: str | None = '测点'
    y_label: str | None = '值'
    x_rotation: int | None = -45
    width: float = 0.35


class PreviewImageRequest(CamelModel):
    chart_x_label: str = 'X 轴'
    chart_y_label: str = 'Y 轴'
    chart_time_range: str = '10T'
    chart_x_rotation: int = 0
    chart_name: str = '示例图'
    chart_line_width: float = 1
    chart_data_number: int = 1000
    chart_fill: ChartFillEnum | None = None
    chart_show_grid: bool = True
