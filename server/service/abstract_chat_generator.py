import os
from abc import abstractmethod
from datetime import datetime

import numpy as np
import pandas as pd
from openpyxl.utils import get_column_letter
from sqlalchemy.orm import Session

import constant
import utils
from schema.task import TaskGenerator
from service.load_csv_file import LoadCsvFile
from utils import get_now_date


class AbstractChatGenerator:

    def __init__(self, data: LoadCsvFile, generator: TaskGenerator, db: Session, excel_name: str):
        self.files = generator.files.split(constant.GENERATOR_FILE_SEPARATOR)
        self.db = db
        self.generator = generator
        self.output = '' if generator.output is None else generator.output
        self.keys = data.data.keys()
        self.data = data.data
        self.times = data.times
        self.dau_config = data.dau_config
        self.new_columns = data.new_columns
        self.dir = os.path.join(constant.ROOT_DIRECTORY, generator.name)
        self.excel_name = excel_name
        self.type = ''

    def write_log(self):
        self.db.query(TaskGenerator).filter_by(id=self.generator.id).update({
            TaskGenerator.output: self.output,
            TaskGenerator.updated_date: datetime.now()
        })
        self.db.commit()

    def generate_table(self, sub_dir="数据表格"):
        """
        生成数据表格
        :param sub_dir: 子文件夹名称
        :return:
        """
        self.output += f"[{get_now_date()}] 开始生成 {self.excel_name}"
        path = os.path.join(self.dir, sub_dir)
        if not os.path.exists(path):
            os.makedirs(path)
        table_result = self.get_table_data()
        df = pd.DataFrame(table_result)
        # 存入到 excel
        filename = os.path.join(path, self.excel_name)
        if os.path.exists(filename):
            filename = os.path.join(path, utils.get_file_now_date() + self.excel_name)
        with pd.ExcelWriter(filename, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Sheet1', index=False)

            # 表格宽度自适应
            column_widths = (
                df.columns.to_series().apply(lambda x: len(str(x).encode('gbk'))).values
            )
            max_widths = (
                df.astype(str).map(lambda x: len(str(x).encode('gbk'))).agg("max").values
            )
            widths = np.max([column_widths, max_widths], axis=0)
            worksheet = writer.sheets['Sheet1']
            for i, width in enumerate(widths, 1):
                worksheet.column_dimensions[get_column_letter(i)].width = width + 2
        self.output += f"[{get_now_date()}] {self.excel_name} 生成完毕"
        return self

    def get_table_data(self):
        table_result = []
        # 获取到数据
        dau_install_no_list = self.dau_config.keys()
        for table_key in self.data.keys():
            if utils.check_invalid_column(table_key):
                continue

            numeric = pd.to_numeric(self.data[table_key], errors='coerce')
            column_data = numeric.dropna()
            nan_values = numeric[numeric.isna()]
            if nan_values is not None and len(nan_values) > 0:
                self.output += f"\n[{get_now_date()}] 存在不合法的数据 \n {nan_values} \n"

            table_value = self._table_data_resampled(column_data)
            # 在这里调用 filter_series 方法
            table_value = self.filter_series(table_value)

            # 检查 table_value 是否为空
            if table_value.empty:
                max_value = None
                max_time = None
                min_value = None
                min_time = None
                change = None
            else:
                max_time = table_value.idxmax()
                min_time = table_value.idxmin()

                # 检查 max_time 和 min_time 是否为 NaT
                if pd.isna(max_time) or pd.isna(min_time):
                    max_value = None
                    min_value = None
                    change = None
                else:
                    max_value = table_value.loc[max_time]
                    min_value = table_value.loc[min_time]
                    change = max_value - min_value

            install_location = ''
            if table_key in dau_install_no_list:
                install_location = self.dau_config[table_key]['installLocation']

            table_result.append({
                "编号": table_key,
                "最大值数值": max_value,
                "最大值时间": max_time,
                "最小值数值": min_value,
                "最小值时间": min_time,
                "变化量": change,
                '安装位置': install_location
            })
        return table_result

    @abstractmethod
    def _table_data_resampled(self, df):
        return df

    @abstractmethod
    def filter_series(self, series):
        return series
