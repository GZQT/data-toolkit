import os.path
from abc import ABC, abstractmethod

import numpy as np
import pandas as pd
from matplotlib import dates as mdates
from matplotlib import pyplot as plt
from sqlalchemy.orm import Session

import utils
from constant import logger
from dto.generator import TaskGeneratorStartRequest, ChartFillEnum, GeneratorDataConditionType, GeneratorConfigRequest
from schema.task import TaskGenerator
from service.abstract_chat_generator import AbstractChatGenerator
from service.load_csv_file import LoadCsvFile
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
    def __init__(self, data: LoadCsvFile, generator: TaskGenerator, db: Session, request: TaskGeneratorStartRequest,
                 excel_name: str):
        self.line_chart = request.average_line_chart
        self.request = request
        self.columns_index = []
        self.type = "平均值"
        super().__init__(data, generator, db, excel_name)

    def filter_series(self, series):
        config_obj = self.request.config

        if not config_obj or len(config_obj.converters) == 0:
            logger.info("不存在阈值配置 1")
            return series  # 返回原始 series

        converters = config_obj.converters

        if not converters or len(converters) == 0:
            logger.info("不存在阈值配置 2")
            return series  # 返回原始 series

        for convert in converters:
            key = convert.column_key
            if key in self.new_columns:
                key = self.new_columns[key]
            if key != series.name:
                continue
            for condition in convert.conditions:
                mask_in_range = (series.index >= condition.start_time) & (series.index <= condition.end_time)
                if condition.type == GeneratorDataConditionType.MAX:
                    mask_exceeds = series >= condition.value
                    series[mask_in_range & mask_exceeds] = np.nan
                elif condition.type == GeneratorDataConditionType.MIN:
                    mask_below = series <= condition.value
                    series[mask_in_range & mask_below] = np.nan
                logger.info(
                    f"列 '{convert.column_key}' 存在阈值限制 {condition.type}-{condition.start_time}-{condition.end_time}-{condition.value}\n")
                self.output += f"[{get_now_date()}] 列 '{convert.column_key}' 存在阈值限制 {condition.type}-{condition.start_time}-{condition.end_time}-{condition.value}\n"

        return series  # 返回过滤后的 series

    def draw_line_chart(self, sub_dir):
        path = os.path.join(self.dir, sub_dir)
        if not os.path.exists(path):
            os.makedirs(path)
        for index, line_key in enumerate(self.data.keys()):
            positions = np.where(self.keys == line_key)
            position = positions[0][0] if positions[0].size > 0 else -1
            if len(self.columns_index) > 0 and position not in self.columns_index:
                self.output += f"[{get_now_date()}] {line_key} 需要跳过\n"
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
        if utils.check_invalid_column(line_key):
            self.output += f"[{get_now_date()}] {line_key} 需要跳过\n"
            return
        if index >= len(self.line_chart.name):
            chart_name = f"{self.type}时程曲线图"
        else:
            chart_name = self.line_chart.name[index]
        file_path = f'{os.path.join(path, line_key + chart_name).replace("/", "-")}.png'
        if os.path.exists(file_path):
            file_path = f'{os.path.join(path, utils.get_file_now_date() + "_" + line_key + chart_name).replace("/", "-")}.png'
        # np_datum = np.array(self.data[line_key])
        # df = pd.DataFrame({'time': self.times, 'data': np_datum})
        df = self.data[line_key]
        if len(df) == 0:
            self.output += f"[{get_now_date()}] 列 {line_key} 没有数据，需要跳过\n"
            return

        numeric = pd.to_numeric(df, errors='coerce')
        column_data = numeric.dropna()
        nan_values = numeric[numeric.isna()]
        if nan_values is not None and len(nan_values) > 0:
            self.output += f"\n[{get_now_date()}] 存在不合法的数据 \n {nan_values} \n"
        if len(column_data) == 0:
            self.output += f"[{get_now_date()}] 列转化为数字后 {line_key} 没有数据，需要跳过\n"
            return

        plt.figure(figsize=(10, 5))
        self._resampled_plot(column_data)
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
        logger.info(f"生成完毕 {line_key} {self.type}图{chart_name}")
        self.output += f"[{get_now_date()}] {os.path.basename(file_path)} 生成成功\n"

    @abstractmethod
    def _resampled_plot(self, df):
        pass

    def _init(self, line_chart, name):
        self.output += f"\n[{get_now_date()}] 开始生成{name}折线图"
        self.line_chart = line_chart
        if self.line_chart.column_index is None:
            self.columns_index = []
            self.output += f"\n[{get_now_date()}] {name}生成所有列"
            logger.info(f"{self.generator.name} {name}生成所有列")
        else:
            self.columns_index = self.line_chart.column_index
            self.output += f"\n[{get_now_date()}] {name}生成列 {self.columns_index}"
            logger.info(f"{self.generator.name} {name}生成列 {self.columns_index}")
        self.type = name
        if self.request.save_data:
            filename = os.path.join(self.dir, f"{name}处理后数据.csv")
            csv_data = self._table_data_resampled(self.data)
            time_column = 'time' if 'time' in csv_data.columns else 'col0'
            csv_data[time_column] = csv_data[time_column].dt.strftime('%Y-%m-%d-%H-%M-%S.%f')
            csv_data.to_csv(filename, index=False)


class AverageLineChartGenerator(AbstractLineChatGenerator, ABC):
    def __init__(self, data: LoadCsvFile, generator: TaskGenerator, request: TaskGeneratorStartRequest, db: Session):
        super().__init__(data, generator, db, request, '平均值数据统计.xlsx')
        super()._init(self.request.average_line_chart, "平均值")

    def draw_line_chart(self, sub_dir="平均值折线图"):
        super().draw_line_chart(sub_dir)
        return self

    def _resampled_plot(self, df):
        resampled = self._table_data_resampled(df)
        resampled = super().filter_series(resampled)
        plt.plot(resampled.index, resampled, label='平均值', marker='',
                 linewidth=self.line_chart.line_width)

    def _table_data_resampled(self, df):
        resampled = df.resample(self.line_chart.time_range).mean()
        return fill_data(self.line_chart.fill, resampled)


class MaxMinLineChartGenerator(AbstractLineChatGenerator, ABC):
    def __init__(self, data: LoadCsvFile, generator: TaskGenerator, request: TaskGeneratorStartRequest, db: Session):
        super().__init__(data, generator, db, request, '最大最小值数据统计.xlsx')
        super()._init(self.request.max_min_line_chart, "最大最小值")

    def draw_line_chart(self, sub_dir="最大最小值折线图"):
        super().draw_line_chart(sub_dir)
        return self

    def _resampled_plot(self, df):
        df = super().filter_series(df)
        resampled = df.resample(self.line_chart.time_range).agg(['min', 'max'])
        plt.plot(resampled.index, resampled['min'], label='最小值', marker='',
                 linewidth=self.line_chart.line_width)
        plt.plot(resampled.index, resampled['max'], label='最大值', marker='',
                 linewidth=self.line_chart.line_width)

    def _table_data_resampled(self, df):
        return fill_data(self.line_chart.fill, df)


class RootMeanSquareLineChartGenerator(AbstractLineChatGenerator, ABC):
    def __init__(self, data: LoadCsvFile, generator: TaskGenerator, request: TaskGeneratorStartRequest, db: Session):
        super().__init__(data, generator, db, request, '均方根数据统计.xlsx')
        super()._init(self.request.root_mean_square_line_chart, "均方根")

    def draw_line_chart(self, sub_dir="均方根折线图"):
        super().draw_line_chart(sub_dir)
        return self

    def _resampled_plot(self, df):
        resampled = self._table_data_resampled(df)
        resampled = super().filter_series(resampled)
        plt.plot(resampled.index, resampled, label='均方根', marker='',
                 linewidth=self.line_chart.line_width)

    def _table_data_resampled(self, df):
        resampled = df.resample(self.line_chart.time_range).apply(self._rms)
        return fill_data(self.line_chart.fill, resampled)

    @staticmethod
    def _rms(series):
        if utils.check_invalid_column(series.name):
            if series.empty:
                return np.nan
            return series.iloc[0]
        series = pd.to_numeric(series, errors='coerce')
        series = series.dropna()
        if len(series) == 0:
            return np.nan
        return np.sqrt(np.mean(np.square(series)))


class RawLineChartGenerator(AbstractLineChatGenerator, ABC):

    def __init__(self, data: LoadCsvFile, generator: TaskGenerator, request: TaskGeneratorStartRequest, db: Session):
        super().__init__(data, generator, db, request, '原始值数据统计.xlsx')
        super()._init(self.request.root_mean_square_line_chart, "")

    def draw_line_chart(self, sub_dir="原始值折线图"):
        super().draw_line_chart(sub_dir)
        return self

    def _resampled_plot(self, df):
        resampled = self._table_data_resampled(df)
        resampled = super().filter_series(resampled)
        plt.plot(resampled.index, resampled, label='数值', marker='',
                 linewidth=self.line_chart.line_width)

    def _table_data_resampled(self, df):
        return fill_data(self.line_chart.fill, df)
