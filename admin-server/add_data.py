import os.path
import re

import pandas as pd
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, Float, TIMESTAMP, PrimaryKeyConstraint
from sqlalchemy.exc import ProgrammingError

import utils


def extract_name_part(filename: str) -> str | None:
    # 使用正则表达式匹配所需部分
    match = re.match(r'^(.*)_\d{8}\.csv$', filename)
    if match:
        return match.group(1)
    else:
        return None


def filter_columns(file_abs_path: str, keyword: str) -> list:
    try:
        data = pd.read_csv(file_abs_path, nrows=0)
        columns = data.columns.tolist()
        filtered_columns = [data_col for data_col in columns if keyword in data_col]
        return filtered_columns
    except Exception as e:
        print(f"Error reading the file: {e}")
        return []


def create_table_if_not_exists(engine, table_name, columns):
    metadata = MetaData()
    cols = [Column('id', Integer, primary_key=True, autoincrement=True),
            Column('col0', TIMESTAMP, primary_key=True)]
    cols += [Column(col, Float) for col in columns if col != 'col0']

    table = Table(
        table_name,
        metadata,
        *cols,
        PrimaryKeyConstraint('id', 'col0')
    )

    try:
        table.create(engine, checkfirst=True)
    except ProgrammingError as e:
        print(f"Error creating table: {e}")


base_dir = 'C:\\Users\\zyue\\Documents\\桥梁数据\\孟寨\\第二季度'
csv_files = [
    'data_dau_ma_l_03_通用采集仪_20240430.csv',
    'data_dau_ma_l_03_通用采集仪_20240531.csv',
    'data_dau_ma_l_03_通用采集仪_20240630.csv',
    'data_dau_mz_l_01_通用采集仪_20240430.csv',
    'data_dau_mz_l_01_通用采集仪_20240531.csv',
    'data_dau_mz_l_01_通用采集仪_20240630.csv',
    'data_dau_mz_l_02_通用采集仪_20240430.csv',
    'data_dau_mz_l_02_通用采集仪_20240531.csv',
    'data_dau_mz_l_02_通用采集仪_20240630.csv',
    'data_dau_mz_r_01_通用采集仪_20240430.csv',
    'data_dau_mz_r_01_通用采集仪_20240531.csv',
    'data_dau_mz_r_01_通用采集仪_20240630.csv',
    'data_dau_mz_r_02_通用采集仪_20240430.csv',
    'data_dau_mz_r_02_通用采集仪_20240531.csv',
    'data_dau_mz_r_02_通用采集仪_20240630.csv',
    'data_dau_mz_r_03_通用采集仪_20240430.csv',
    'data_dau_mz_r_03_通用采集仪_20240531.csv',
    'data_dau_mz_r_03_通用采集仪_20240630.csv',
]

if __name__ == '__main__':
    engine = create_engine('postgresql://postgres:123456@192.168.68.225:5432/postgres')

    for file in csv_files:
        file_path = os.path.join(base_dir, file)
        df = pd.read_csv(file_path, low_memory=False)
        print(f"[{utils.get_now_date()}] 读取完成 {file_path}")

        df['col0'] = pd.to_datetime(df['col0'], format='%Y-%m-%d-%H-%M-%S.%f', errors='coerce')
        df = df.dropna(subset=['col0'])

        expected_columns = filter_columns(file_path, 'col')
        print(f"[{utils.get_now_date()}] 列名数组 {expected_columns}")

        for col in expected_columns:
            if col not in df.columns:
                df[col] = pd.NA
        df = df[expected_columns]

        table_name = extract_name_part(file)
        if table_name:
            create_table_if_not_exists(engine, table_name, expected_columns)
            print(f"[{utils.get_now_date()}] 插入数据")
            df.to_sql(table_name, engine, if_exists='append', index=False)
            print(f"[{utils.get_now_date()}] 操作完成")
