import json
import os

import numexpr as ne
import pandas as pd
import requests

from constant import GENERATOR_FILE_SEPARATOR, CSV_SUFFIX, CONFIG_FILE, logger
from dto.generator import GeneratorConfigRequest
from utils import get_now_date


class LoadCsvFile:
    def __init__(self, files):
        self.output = ""
        self.files = []
        for file_path in files.split(GENERATOR_FILE_SEPARATOR):
            if not os.path.exists(file_path):
                self.output += f"[{get_now_date()}] 文件 {os.path.basename(file_path)} 不存在\n"
            elif not file_path.endswith(CSV_SUFFIX):
                self.output += f"[{get_now_date()}] 文件 {os.path.basename(file_path)} 不是 csv 类型\n"
            else:
                self.files.append(file_path)
        self.keys = []
        self.data = {}
        self.times = []

    def load_data(self, generator_config: GeneratorConfigRequest = None):
        data_frames_list = [pd.read_csv(file) for file in self.files]
        combined_df = pd.concat(data_frames_list, ignore_index=True)
        # 忽略 'id' 列和任何以 'Unnamed' 开头的列
        # combined_df = combined_df.loc[:, ~combined_df.columns.str.contains('^Unnamed|^id')]
        # 确定时间列，优先考虑 'time'，如果不存在则使用 'col0'
        time_column = 'time' if 'time' in combined_df.columns else 'col0'
        # 确保时间列存在
        if time_column not in combined_df.columns:
            self.output += f"[{get_now_date()}] 读取数据中不存在 time 或者 col0 的时间列\n"
            return self
        combined_df[time_column] = pd.to_datetime(combined_df[time_column], format='%Y-%m-%d-%H-%M-%S.%f')
        combined_df.set_index(combined_df[time_column], inplace=True)
        # 使用 numexpr 库对每一列执行相应的表达式
        self.apply_expressions(combined_df, generator_config)
        self.times = combined_df[time_column]
        self.data = combined_df
        self.apply_dau_config(combined_df, generator_config)
        return self

    def apply_expressions(self, combined_df, generator_config):
        """
        应用表达式到数据框的列，并生成安全列名映射
        """
        if generator_config is None:
            return
        key_converters = {converter.column_key: converter.expression for converter in generator_config.converters}

        # 生成安全列名映射
        filtered_columns = [col for col in combined_df.columns if col != 'id']
        safe_columns = {col: f'c{i}' for i, col in enumerate(filtered_columns)}
        reverse_safe_columns = {v: k for k, v in safe_columns.items()}
        local_dict = {safe_columns[col]: combined_df[col] for col in filtered_columns}
        temp_df = combined_df.copy()
        # 使用安全列名进行表达式替换
        temp_df.rename(columns=safe_columns, inplace=True)
        for column_key, expression in key_converters.items():
            if expression == '':
                self.output += f"[{get_now_date()}] 列 '{column_key}' 不需要进行数据预操作\n"
                continue
            safe_col_key = safe_columns[column_key]
            if safe_col_key in temp_df.columns:
                for i, safe_col in enumerate(safe_columns.values()):
                    expression = expression.replace(f'c{i}', safe_col)

                try:
                    temp_df[safe_col_key] = ne.evaluate(expression, local_dict=local_dict)
                    self.output += f"[{get_now_date()}] 计算列 '{column_key}' 的表达式 {expression} 成功\n"
                except Exception as e:
                    self.output += f"[{get_now_date()}] 计算列 '{column_key}' 的表达式 {expression} 时出错: {e}\n"
            else:
                self.output += f"[{get_now_date()}] 列 '{column_key}' 转化为后 '{safe_col_key}' 不存在于数据中\n"

        # 还原列名
        temp_df.rename(columns=reverse_safe_columns, inplace=True)
        combined_df.update(temp_df)

    def apply_dau_config(self, combined_df, generator_config):
        if generator_config is None or generator_config.dau_config is None:
            return
        try:
            with open(CONFIG_FILE, 'r', encoding='utf-8') as file:
                config = json.load(file)
        except FileNotFoundError:
            self.output += f"未找到配置文件 {CONFIG_FILE}"
            logger.warning(f"File not found: {CONFIG_FILE}")
            return
        except json.JSONDecodeError:
            self.output += f"错误的文件格式 {CONFIG_FILE}"
            logger.warning(f"Error decoding JSON in file: {CONFIG_FILE}")
            return

        id_list = [config.mapping for config in generator_config.dau_config]

        remote_server = config['remoteServer']
        response = requests.get(f"{remote_server}/dau/ids", params={
            "ids": id_list
        })
        if response.status_code != 200:
            self.output += f"远程服务请求错误 {remote_server} {response.status_code}"
            logger.warning(f"Remote server error {remote_server} {response.status_code} {response.text}")
            return
        body = response.json()
        self.output += f"获取远程服务 DAU 配置结果 \n {body}"
        mapping = {}
        for item in body:
            mapping[item["id"]] = item["installNo"]
        all_keys = mapping.keys()
        new_columns = {}
        for config in generator_config.dau_config:
            if config.mapping not in all_keys:
                self.output += f"列映射 {config.column} {config.mapping} 数据不存在"
                continue
            mapping_column = mapping[config.mapping]
            self.output += f"更改列名称 {config.column} 为 {mapping_column}"
            new_columns[config.column] = mapping_column
        combined_df.rename(columns=new_columns, inplace=True)
        self.data = combined_df
        self.output += f"列名称更改完成"
