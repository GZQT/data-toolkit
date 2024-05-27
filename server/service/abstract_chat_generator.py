import os
from abc import abstractmethod
from datetime import datetime

import numpy as np
import pandas as pd
from openpyxl.utils import get_column_letter
from sqlalchemy.orm import Session

from constant import GENERATOR_FILE_SEPARATOR, ROOT_DIRECTORY, CSV_SUFFIX
from schema.task import TaskGenerator
from service.load_csv_file import LoadCsvFile
from utils import get_csv_data_file, get_now_date


class AbstractChatGenerator:

    def __init__(self, data: LoadCsvFile, generator: TaskGenerator, db: Session, excel_name: str):
        self.files = generator.files.split(GENERATOR_FILE_SEPARATOR)
        self.db = db
        self.generator = generator
        self.output = '' if generator.output is None else generator.output
        self.keys = data.data.keys()
        self.data = data.data
        self.times = data.times
        self.dir = os.path.join(ROOT_DIRECTORY, generator.name)
        self.excel_name = excel_name

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
        with pd.ExcelWriter(os.path.join(path, self.excel_name), engine='openpyxl') as writer:
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
        for table_key in self.data.keys():
            if table_key == "time" or table_key == 'col0':
                continue
            table_value = self._table_data_resampled(self.data[table_key])
            max_time = table_value.idxmax()
            min_time = table_value.idxmin()
            table_result.append({
                "编号": table_key,
                "最大值数值": table_value.loc[max_time],
                "最大值时间": max_time,
                "最小值数值": table_value.loc[min_time],
                "最小值时间": min_time,
                "变化量": table_value.loc[max_time] - table_value.loc[min_time]
            })
        return table_result

    @abstractmethod
    def _table_data_resampled(self, df):
        return df
