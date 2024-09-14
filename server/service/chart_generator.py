import json
import os
import traceback
from datetime import datetime
from typing import List

from sqlalchemy.orm import Session

import constant
from constant import logger
from dto.generator import TaskGeneratorStartRequest, GeneratorResultEnum, BarChartGeneratorStartRequest, DauConfig, \
    GeneratorConfigRequest
from schema.task import TaskGenerator
from service.abstract_chat_generator import AbstractChatGenerator
from service.bar_chart_generator import MaxMinBarChartGenerator, draw_compare_bar_chart
from service.line_chart_generator import AverageLineChartGenerator, MaxMinLineChartGenerator, \
    RootMeanSquareLineChartGenerator, RawLineChartGenerator
from service.load_csv_file import LoadCsvFile
from utils import get_now_date


def _generate_chart(db: Session, data, generator: TaskGenerator, request: TaskGeneratorStartRequest):
    generator.output += data.output
    average_generator: AbstractChatGenerator | None = None
    max_min_generator: AbstractChatGenerator | None = None
    root_mean_square_generator: AbstractChatGenerator | None = None
    raw_generator: AbstractChatGenerator | None = None
    if request.average_line_chart.generate:
        average_generator = AverageLineChartGenerator(data, generator, request, db).draw_line_chart()
        generator.output = average_generator.output
    if request.root_mean_square_line_chart.generate:
        average_generator = RootMeanSquareLineChartGenerator(data, generator, request, db).draw_line_chart()
        generator.output = average_generator.output
    if request.max_min_line_chart.generate:
        max_min_generator = MaxMinLineChartGenerator(data, generator, request, db).draw_line_chart()
        generator.output = max_min_generator.output
    if request.raw_line_chart.generate:
        raw_generator = RawLineChartGenerator(data, generator, request, db).draw_line_chart()
        generator.output = raw_generator.output
    if request.max_min_bar_chart:
        max_min_generator = MaxMinBarChartGenerator(data, generator, db).draw_bar_chart(request.max_min_bar_group)
        generator.output = max_min_generator.output
    if request.average_data_table:
        if average_generator is not None:
            average_generator.generate_table()
        else:
            average_generator = AverageLineChartGenerator(data, generator, request, db).generate_table()
        generator.output = average_generator.output
    if request.max_min_data_table:
        if max_min_generator is not None:
            max_min_generator = max_min_generator.generate_table()
        else:
            max_min_generator = MaxMinLineChartGenerator(data, generator, request, db).generate_table()
        generator.output = max_min_generator.output
    if request.root_mean_square_data_table:
        if root_mean_square_generator is not None:
            root_mean_square_generator = root_mean_square_generator.generate_table()
        else:
            root_mean_square_generator = \
                RootMeanSquareLineChartGenerator(data, generator, request, db).generate_table()
        generator.output = root_mean_square_generator.output
    if request.raw_data_table:
        if raw_generator is not None:
            raw_generator = raw_generator.generate_table()
        else:
            raw_generator = \
                RawLineChartGenerator(data, generator, request, db).generate_table()
        generator.output = raw_generator.output
    generator.output += f"\n[{get_now_date()}] 任务完成"
    db.query(TaskGenerator).filter_by(id=generator.id).update({
        TaskGenerator.status: GeneratorResultEnum.SUCCESS,
        TaskGenerator.result: f'生成成功',
        TaskGenerator.output: generator.output,
        TaskGenerator.updated_date: datetime.now()
    })
    db.commit()


def _get_generate_config(db, generator, request):
    config: GeneratorConfigRequest | None = None
    if hasattr(request, 'config') and request.config is not None:
        generator.output += \
            f"\n[{get_now_date()}] 检测到有新的配置信息，更新数据库数据\n"
        config = request.config
        db.query(TaskGenerator).filter_by(id=generator.id).update({
            TaskGenerator.config: json.dumps(config.dict()),
            TaskGenerator.output: generator.output,
            TaskGenerator.updated_date: datetime.now()
        })
        db.commit()
    elif generator.config_obj is not None:
        generator.output += \
            f"\n[{get_now_date()}] 检测到存在配置信息，使用原始配置"
        config = GeneratorConfigRequest(**generator.config_obj)
    return config

def generate_chart(generator: TaskGenerator, request: TaskGeneratorStartRequest, db: Session):
    if generator.output is None:
        generator.output = \
            f"\n[{get_now_date()}] 任务开始，接收到的参数为 \n{request.__dict__}\n"
    else:
        generator.output += \
            f"\n[{get_now_date()}] 任务开始，接收到的参数为 \n{request.__dict__}\n"
    db.query(TaskGenerator).filter_by(id=generator.id).update({
        TaskGenerator.status: GeneratorResultEnum.PROCESSING,
        TaskGenerator.output: generator.output,
        TaskGenerator.result: f'生成中...',
        TaskGenerator.updated_date: datetime.now()
    })
    db.commit()

    try:
        config = _get_generate_config(db, generator, request)
        data = LoadCsvFile(generator.files).load_data(config)
        _generate_chart(db, data, generator, request)
    except Exception as e:
        generator.output += \
            f"\n[{get_now_date()}] 生成失败 \n{traceback.format_exc()}"
        traceback.print_exc()
        logger.warning(f"生成失败 {generator.name}")
        logger.exception(e)
        db.query(TaskGenerator).filter_by(id=generator.id).update({
            TaskGenerator.status: GeneratorResultEnum.FAILED,
            TaskGenerator.result: f'生成失败：{str(e)}',
            TaskGenerator.updated_date: datetime.now()
        })
        db.commit()




def generate_bar_chart(generators: List[TaskGenerator] , request: BarChartGeneratorStartRequest, db: Session):
    db.query(TaskGenerator).filter(TaskGenerator.id.in_(request.generator_ids)).update({
        TaskGenerator.status: GeneratorResultEnum.PROCESSING,
        TaskGenerator.result: f"生成对比图中",
        TaskGenerator.updated_date: datetime.now()
    })
    db.commit()
    try:
        compare_group = request.compare_group
        max_min_bar_chart_generator = []
        max_min_data_table = []
        for generator in generators:
            log = f"\n[{get_now_date()}] {generator.name} 开始进行表格数据处理"
            if generator.output is None:
                generator.output = log
            else:
                generator.output += log
            logger.info(f"{generator.name} 开始进行表格数据处理")
            config = _get_generate_config(db, generator, request)
            data = LoadCsvFile(generator.files).load_data(config)
            generator.output += data.output
            db.query(TaskGenerator).filter_by(id=generator.id).update({
                TaskGenerator.output: generator.output,
                TaskGenerator.updated_date: datetime.now()
            })
            db.commit()
            chart_generator = MaxMinBarChartGenerator(data, generator, db)
            max_min_bar_chart_generator.append(chart_generator)
            max_min_data_table.append(chart_generator.get_table_data())
            generator.output += f"\n[{get_now_date()}] 表格数据处理完毕，等待生成对比图"
            logger.info(f"{generator.name} 表格数据处理完毕，等待生成对比图")
            db.query(TaskGenerator).filter_by(id=generator.id).update({
                TaskGenerator.output: generator.output,
                TaskGenerator.updated_date: datetime.now()
            })
            db.commit()
        logger.info("数据全部处理完毕，开始生成对比图")
        db.query(TaskGenerator).filter(TaskGenerator.id.in_(request.generator_ids)).update({
            TaskGenerator.status: GeneratorResultEnum.PROCESSING,
            TaskGenerator.result: f"图表生成中",
            TaskGenerator.updated_date: datetime.now()
        })
        db.commit()
        for compare_list_index, compare_list in enumerate(compare_group):
            data = []
            for compare_table_index, compare_table in enumerate(compare_list):
                table_data = max_min_data_table[compare_table_index]
                chart_generator = max_min_bar_chart_generator[compare_table_index]
                column_names = []
                for compare_column in compare_table:
                    column_names.append(chart_generator.keys[compare_column])
                for row_data in table_data:
                    if row_data['编号'] in column_names:
                        data.append(row_data)
            draw_compare_bar_chart(data, request, compare_list_index)
        db.query(TaskGenerator).filter(TaskGenerator.id.in_(request.generator_ids)).update({
            TaskGenerator.status: GeneratorResultEnum.SUCCESS,
            TaskGenerator.result: f"生成对比成功",
            TaskGenerator.updated_date: datetime.now()
        })
        db.commit()
    except Exception as e:
        traceback.print_exc()
        logger.warning(f"生成对比失败")
        logger.exception(e)
        db.query(TaskGenerator).filter(TaskGenerator.id.in_(request.generator_ids)).update({
            TaskGenerator.status: GeneratorResultEnum.FAILED,
            TaskGenerator.result: f'生成对比失败：{str(e)}',
            TaskGenerator.updated_date: datetime.now()
        })
        db.commit()
