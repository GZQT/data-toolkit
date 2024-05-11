import os
from datetime import datetime

import numpy as np
import pandas as pd
from openpyxl.utils import get_column_letter
from sqlalchemy.orm import Session

from constant import GENERATOR_FILE_SEPARATOR, ROOT_DIRECTORY, CSV_SUFFIX
from schema.task import TaskGenerator
from utils import get_csv_data_file, get_now_date


class AbstractChatGenerator:

    def __init__(self, generator: TaskGenerator, db: Session, excel_name: str):
        self.files = generator.files.split(GENERATOR_FILE_SEPARATOR)
        self.db = db
        self.generator = generator
        self.output = '' if generator.output is None else generator.output
        self.data = {}
        self.times = []
        self.dir = os.path.join(ROOT_DIRECTORY, generator.name)
        self.excel_name = excel_name
        self.keys = []
        self._load_data()

    def _load_data(self):
        for file in self.files:
            if not file.endswith(CSV_SUFFIX):
                self.output += f"[{get_now_date()}] 文件 {os.path.basename(file)} 不是 csv 类型\n"
                continue
            self.output += f"[{get_now_date()}] 正在处理文件 {os.path.basename(file)}...\n"
            for item in get_csv_data_file(file):
                for key in item:
                    self.keys.append(key)
                    value = 0 if item[key] is None else item[key]
                    if key == 'id' or key.startswith('Unnamed'):
                        continue
                    elif key == 'col0' or key == 'time':
                        self.times.append(datetime.strptime(value, "%Y-%m-%d-%H-%M-%S.%f"))
                    elif key in self.data:
                        self.data[key].append(value)
                    else:
                        self.data[key] = [value]
            self.output += f"[{get_now_date()}] 文件 {os.path.basename(file)} 处理完毕\n"
            self.write_log()

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
            table_value = self.data[table_key]
            max_value = max(table_value)
            min_value = min(table_value)
            table_result.append({
                "编号": table_key,
                "最大值数值": max_value,
                "最大值时间": self.times[table_value.index(max_value)],
                "最小值数值": min_value,
                "最小值时间": self.times[table_value.index(min_value)],
                "变化量": max_value - min_value
            })
        return table_result
