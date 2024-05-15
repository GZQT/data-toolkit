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
        self.line_chart = request.average_line_chart
        self.request = request
        self.columns_index = []
        self.type = "平均值"

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
        if index >= len(self.line_chart.name):
            chart_name = f"{self.type}时程曲线图"
        else:
            chart_name = self.line_chart.name[index]
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
        plt.xlabel(self.line_chart.x_label)
        plt.ylabel(self.line_chart.y_label)
        plt.legend()
        plt.grid(self.line_chart.show_grid)
        rotation = self.line_chart.x_rotation
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

    def _init(self, line_chart, name):
        self.output += f"[{get_now_date()}] 开始生成{name}折线图"
        self.line_chart = line_chart
        if self.line_chart.column_index is None:
            self.columns_index = []
            self.output += f"[{get_now_date()}] {name}生成所有列"
            logger.info(f"{self.generator.name} {name}生成所有列")
        else:
            self.columns_index = self.line_chart.column_index
            self.output += f"[{get_now_date()}] {name}生成列 {self.columns_index}"
            logger.info(f"{self.generator.name} {name}生成列 {self.columns_index}")
        self.type = name


class AverageLineChartGenerator(AbstractLineChatGenerator, ABC):
    def __init__(self, generator: TaskGenerator, request: TaskGeneratorStartRequest, db: Session):
        super().__init__(generator, db, request, '平均值数据统计.xlsx')
        super()._init(self.request.average_line_chart, "平均值")

    def draw_line_chart(self, sub_dir="平均值折线图"):
        super().draw_line_chart(sub_dir)
        return self

    def _resampled_plot(self, df):
        resampled = df.resample(self.line_chart.time_range).mean()
        resampled = fill_data(self.line_chart.fill, resampled)
        plt.plot(resampled.index, resampled['data'], label='平均值', marker='',
                 linewidth=self.line_chart.line_width)


class MaxMinLineChartGenerator(AbstractLineChatGenerator, ABC):
    def __init__(self, generator: TaskGenerator, request: TaskGeneratorStartRequest, db: Session):
        super().__init__(generator, db, request, '最大最小值数据统计.xlsx')
        super()._init(self.request.max_min_line_chart, "最大最小值")

    def draw_line_chart(self, sub_dir="最大最小值折线图"):
        super().draw_line_chart(sub_dir)
        return self

    def _resampled_plot(self, df):
        resampled = df.resample(self.line_chart.time_range).agg(['min', 'max'])
        resampled = fill_data(self.line_chart.fill, resampled)
        plt.plot(resampled.index, resampled['data']['min'], label='最小值', marker='',
                 linewidth=self.line_chart.line_width)
        plt.plot(resampled.index, resampled['data']['max'], label='最大值', marker='',
                 linewidth=self.line_chart.line_width)


class RootMeanSquareLineChartGenerator(AbstractLineChatGenerator, ABC):
    def __init__(self, generator: TaskGenerator, request: TaskGeneratorStartRequest, db: Session):
        super().__init__(generator, db, request, '均方根数据统计.xlsx')
        super()._init(self.request.root_mean_square_line_chart, "均方根")

    def draw_line_chart(self, sub_dir="均方根折线图"):
        super().draw_line_chart(sub_dir)
        return self

    def _resampled_plot(self, df):
        resampled = df.resample(self.line_chart.time_range).apply(self._rms)
        resampled = fill_data(self.line_chart.fill, resampled)
        plt.plot(resampled.index, resampled['data'], label='均方根', marker='',
                 linewidth=self.line_chart.line_width)

    @staticmethod
    def _rms(series):
        return np.sqrt(np.mean(np.square(series)))