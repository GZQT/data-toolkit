import os
from abc import ABC

from matplotlib import pyplot as plt
from sqlalchemy.orm import Session

from constant import ROOT_DIRECTORY
from dto.generator import TaskGeneratorStartRequest, BarChartGeneratorStartRequest
from schema.task import TaskGenerator
from service.abstract_chat_generator import AbstractChatGenerator
from service.load_csv_file import LoadCsvFile
from utils import get_now_date

plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False


class MaxMinBarChartGenerator(AbstractChatGenerator, ABC):
    def __init__(self, data: LoadCsvFile, generator: TaskGenerator, db: Session):
        super().__init__(data, generator, db, '最大最小值数据统计.xlsx')
        self.output += f"[{get_now_date()}] 开始生成最大最小值柱状图"

    def draw_bar_chart(self, bar_group, sub_dir="最大最小值柱状图"):
        """
        生成柱状图
        :param sub_dir: 创建子文件夹路径
        :param bar_group:柱状图分组
            [
                [1, 2, 3],
                [4, 5, 6]
            ]
        :return:
        """
        path = os.path.join(self.dir, sub_dir)
        if not os.path.exists(path):
            os.makedirs(path)

        # 读取所有最大最小值和标签
        all_max_values = [max(values) for values in self.data.values()]
        all_min_values = [min(values) for values in self.data.values()]
        all_labels = list(self.data.keys())

        for column_scope in bar_group:
            self._draw_bar_chart(path, all_max_values, all_min_values, all_labels, column_scope)
            super().write_log()
        return self

    def _draw_bar_chart(self, path, all_max_values, all_min_values, all_labels, column_scope):
        chart_name = f"{column_scope} 最大最小值对比图"
        file_path = f'{os.path.join(path, chart_name).replace("/", "-")}.png'
        self.output += f"[{get_now_date()}] {os.path.basename(file_path)} 生成中...\n"

        # 获取指定范围的最大最小值和标签
        max_values = [all_max_values[index - 2] for index in column_scope]
        min_values = [all_min_values[index - 2] for index in column_scope]
        labels = [all_labels[index - 2] for index in column_scope]

        # 创建柱状图
        x = range(len(labels))  # x轴坐标
        width = 0.35  # 柱的宽度

        fig, ax = plt.subplots()
        max_bar = ax.bar(x, max_values, width, label='最大值')
        min_bar = ax.bar([p + width for p in x], min_values, width, label='最小值')

        plt.rcParams['font.size'] = 6
        plt.bar_label(max_bar, label_type='edge')
        plt.bar_label(min_bar, label_type='edge')
        # 添加标签、标题和图例
        ax.set_xlabel('测点')
        ax.set_ylabel('值')
        ax.set_title(f'最大最小值对比图')
        plt.xticks(rotation=-45)
        ax.set_xticks([p + width / 2 for p in x])
        ax.set_xticklabels(labels)
        ax.legend()
        plt.subplots_adjust(bottom=0.4)
        plt.savefig(file_path)
        plt.close()
        self.output += f"[{get_now_date()}] {os.path.basename(file_path)} 生成成功\n"


def draw_compare_bar_chart(data, request: BarChartGeneratorStartRequest, index: int):
    max_values = []
    min_values = []
    labels = []
    for item in data:
        max_values.append(item['最大值数值'])
        min_values.append(item['最小值数值'])
        labels.append(item['编号'])
    chart_name = "对比图" if request.chart_name is None else request.chart_name
    max_min_dir = os.path.join(ROOT_DIRECTORY, "最大最小值对比图")
    if not os.path.exists(max_min_dir):
        os.makedirs(max_min_dir)
    if index == 0:
        file_path = f'{os.path.join(ROOT_DIRECTORY, "最大最小值对比图", f"{chart_name}").replace("/", "-")}.png'
    else:
        file_path = f'{os.path.join(ROOT_DIRECTORY, "最大最小值对比图", f"{chart_name}-{index}").replace("/", "-")}.png'
    x = range(len(labels))
    width = request.width
    fig, ax = plt.subplots()
    max_bar = ax.bar(x, max_values, width, label='最大值')
    min_bar = ax.bar([p + width for p in x], min_values, width, label='最小值')
    plt.rcParams['font.size'] = 6
    plt.bar_label(max_bar, label_type='edge')
    plt.bar_label(min_bar, label_type='edge')
    if request.x_label:
        ax.set_xlabel(request.x_label)
    if request.y_label:
        ax.set_ylabel(request.y_label)
    ax.set_title("最大最小值对比图")
    if request.x_rotation < 0:
        plt.xticks(rotation=request.x_rotation, ha='left')
    elif request.x_rotation > 0:
        plt.xticks(rotation=request.x_rotation, ha='right')
    ax.set_xticks([p + width / 2 for p in x])
    ax.set_xticklabels(labels)
    ax.legend(loc='upper left', bbox_to_anchor=(1, 1))
    plt.subplots_adjust(bottom=0.4)
    plt.tight_layout()
    plt.savefig(file_path)
    plt.close()
