import os.path
from abc import ABC, abstractmethod

import numpy as np
import pandas as pd
from matplotlib import dates as mdates
from matplotlib import pyplot as plt
from sqlalchemy.orm import Session

from constant import logger
from dto.generator import TaskGeneratorStartRequest, ChartFillEnum
from schema.task import TaskGenerator
from service.abstract_chat_generator import AbstractChatGenerator
from utils import get_now_date

plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False


def fill_data(fill_method, resampled):
    if fill_method == ChartFillEnum.FORWARD_FILL:
        return resampled.fillna(method='ffill')
    elif fill_method == ChartFillEnum.BACKWARD_FILL:
        return resampled.fillna(method='bfill')
    elif fill_method == ChartFillEnum.LINE:
        return resampled.interpolate(method='linear')
    # elif fill_method == ChartFillEnum.NEAREST_NEIGHBOR:
    #     return resampled.interpolate(method='nearest')
    elif fill_method == ChartFillEnum.TIME:
        return resampled.interpolate(method='time')
    # elif fill_method == ChartFillEnum.SPLINE:
    #     return resampled.interpolate(method='spline', order=3)
    # elif fill_method == ChartFillEnum.SPLINE:
    #     return resampled.interpolate(method='polynomial', order=2)
    else:
        return resampled


class AbstractLineChatGenerator(AbstractChatGenerator, ABC):
    def __init__(self, generator: TaskGenerator, db: Session, request: TaskGeneratorStartRequest, excel_name: str):
        super().__init__(generator, db, '平均值数据统计.xlsx')
        self.request = request
        self.columns_index = []
        self.line_chart_line_width = 1
        self.line_chart_time_range = "10min"
        self.line_chart_x_label = "时间"
        self.line_chart_y_label = "值"
        self.line_chart_show_grid = True
        self.line_chart_x_rotation = 90
        self.line_chart_fill = None
        self.line_chart_name = "时程曲线图"
        self.type = "最大最小值"

    def draw_line_chart(self, sub_dir):
        path = os.path.join(self.dir, sub_dir)
        if not os.path.exists(path):
            os.makedirs(path)
        for index, line_key in enumerate(self.data.keys()):
            if len(self.columns_index) > 0 and self.keys.index(line_key) not in self.columns_index:
                self.output += f"[{get_now_date()}] {line_key} 需要跳过"
                logger.info(f"{line_key} 折线图需要跳过")
            elif len(self.data[line_key]) != len(self.times):
                self.output += \
                    f"[{get_now_date()}] {line_key} 数据长度和时间长度不匹配 {len(self.data[line_key])} {len(self.times)}\n"
                logger.warning(f"{line_key} 数据长度和时间长度不匹配 {len(self.data[line_key])} {len(self.times)}")
            else:
                self._draw_line_chart(path, line_key, index)
            self.write_log()
        return self

    def _draw_line_chart(self, path, line_key, index):
        if index >= len(self.line_chart_name):
            chart_name = f"{self.type}时程曲线图"
        else:
            chart_name = self.line_chart_name[index]
        logger.info(f"开始生成{self.type}图 {chart_name}")
        file_path = f'{os.path.join(path, line_key + chart_name).replace("/", "-")}.png'
        self.output += f"[{get_now_date()}] {os.path.basename(file_path)} 生成中...\n"
        np_datum = np.array(self.data[line_key])
        df = pd.DataFrame({'time': self.times, 'data': np_datum})
        df.set_index('time', inplace=True)
        plt.figure(figsize=(10, 5))
        self._resampled_plot(df)
        date_format = mdates.DateFormatter('%Y%m%d')
        plt.gca().xaxis.set_major_formatter(date_format)
        plt.title(chart_name)
        plt.xlabel(self.line_chart_x_label)
        plt.ylabel(self.line_chart_y_label)
        plt.legend()
        plt.grid(self.line_chart_show_grid)
        rotation = self.line_chart_x_rotation
        if rotation < 0:
            plt.xticks(rotation=rotation, ha='left')
        elif rotation > 0:
            plt.xticks(rotation=rotation, ha='right')
        plt.tight_layout()
        plt.savefig(file_path)
        plt.close()
        logger.info(f"生成完毕 {chart_name}")
        self.output += f"[{get_now_date()}] {os.path.basename(file_path)} 生成成功\n"

    @abstractmethod
    def _resampled_plot(self, df):
        pass


class AverageLineChartGenerator(AbstractLineChatGenerator, ABC):
    def __init__(self, generator: TaskGenerator, request: TaskGeneratorStartRequest, db: Session):
        super().__init__(generator, db, request, '平均值数据统计.xlsx')
        self.output += f"[{get_now_date()}] 开始生成平均值折线图"
        if self.request.average_line_chart_column_index is None:
            self.columns_index = []
            self.output += f"[{get_now_date()}] 平均值生成所有列"
            logger.info(f"{generator.name} 平均值生成所有列")
        else:
            self.columns_index = self.request.average_line_chart_column_index
            self.output += f"[{get_now_date()}] 平均值生成列 {self.columns_index}"
            logger.info(f"{generator.name} 平均值生成列 {self.columns_index}")
        self.line_chart_line_width = self.request.average_line_chart_line_width
        self.line_chart_time_range = self.request.average_line_chart_time_range
        self.line_chart_x_label = self.request.average_line_chart_x_label
        self.line_chart_y_label = self.request.average_line_chart_y_label
        self.line_chart_show_grid = self.request.average_line_chart_show_grid
        self.line_chart_x_rotation = self.request.average_line_chart_x_rotation
        self.line_chart_name = self.request.average_line_chart_name
        self.line_chart_fill = self.request.average_line_chart_fill
        self.type = "平均值"

    def draw_line_chart(self, sub_dir="平均值折线图"):
        super().draw_line_chart(sub_dir)
        return self

    def _resampled_plot(self, df):
        resampled = df.resample(self.line_chart_time_range).agg(['min', 'max'])
        resampled = fill_data(self.line_chart_fill, resampled)
        plt.plot(resampled.index, resampled['data'], label='平均值', marker='',
                 linewidth=self.request.average_line_chart_line_width)


class MaxMinLineChartGenerator(AbstractLineChatGenerator, ABC):
    def __init__(self, generator: TaskGenerator, request: TaskGeneratorStartRequest, db: Session):
        super().__init__(generator, db, request, '最大最小值数据统计.xlsx')
        self.output += f"[{get_now_date()}] 开始生成最大最小值折线图"
        if self.request.max_min_line_chart_column_index is None:
            self.columns_index = []
            self.output += f"[{get_now_date()}] 最大最小值生成所有列"
            logger.info(f"{generator.name} 最大最小值生成所有列")
        else:
            self.columns_index = self.request.max_min_line_chart_column_index
            self.output += f"[{get_now_date()}] 最大最小值生成列 {self.columns_index}"
            logger.info(f"{generator.name} 最大最小值生成列 {self.columns_index}")
        self.line_chart_line_width = self.request.max_min_line_chart_line_width
        self.line_chart_time_range = self.request.max_min_line_chart_time_range
        self.line_chart_x_label = self.request.max_min_line_chart_x_label
        self.line_chart_y_label = self.request.max_min_line_chart_y_label
        self.line_chart_show_grid = self.request.max_min_line_chart_show_grid
        self.line_chart_x_rotation = self.request.max_min_line_chart_x_rotation
        self.line_chart_name = self.request.max_min_line_chart_name
        self.line_chart_fill = self.request.max_min_line_chart_fill
        self.type = "最大最小值"

    def draw_line_chart(self, sub_dir="最大最小值折线图"):
        super().draw_line_chart(sub_dir)
        return self

    def _resampled_plot(self, df):
        resampled = df.resample(self.line_chart_time_range).agg(['min', 'max'])
        resampled = fill_data(self.line_chart_fill, resampled)
        plt.plot(resampled.index, resampled['data']['min'], label='最小值', marker='',
                 linewidth=self.line_chart_line_width)
        plt.plot(resampled.index, resampled['data']['max'], label='最大值', marker='',
                 linewidth=self.line_chart_line_width)
