from datetime import datetime

import numpy as np
import pandas as pd


def generate_data(start_date, end_date, num_points, data_range):
    # 生成时间序列
    start = datetime.strptime(start_date, "%Y-%m-%d %H:%M:%S")
    end = datetime.strptime(end_date, "%Y-%m-%d %H:%M:%S")
    delta = (end - start) / (num_points - 1)
    time_points = [start + i * delta for i in range(num_points)]

    # 生成数据
    data_points = np.random.randint(data_range[0], data_range[1] + 1, num_points)

    # 返回结果字典
    return {'time': time_points, 'data': data_points.tolist()}


def get_now_date():
    return datetime.now().strftime('%Y-%m-%d %H:%M:%S')


def get_file_now_date():
    return datetime.now().strftime('%Y%m%d%H%M%S')


def detect_encoding(file_path):
    encodings = ['utf-8', 'utf-8-sig', 'ansi']
    for encoding in encodings:
        try:
            return pd.read_csv(file_path, encoding=encoding)
        except UnicodeDecodeError:
            continue
    return None


def get_csv_data_file(file):
    try:
        if not file.endswith('.csv'):
            print(f"{file} 不是 csv，跳过")
            return
        df = detect_encoding(file)
        return df.to_dict(orient='records')
    except Exception as e:
        print(f"{file} 文件读取出错:", e)


def is_number(variable):
    return isinstance(variable, (int, float))


def check_invalid_column(line_key):
    if line_key == 'time' or line_key == 'col0' or line_key == 'id' or 'Unnamed' in line_key:
        return True
    return False


def get_time_column(df):
    for col in df.columns:
        if col in ['col0', 'time']:
            return col
    return None


def remove_last_underscore(text):
    # 找到最后一个下划线的位置
    last_underscore_index = text.rfind('_')
    # 如果存在下划线，则移除下划线及其后的内容
    if last_underscore_index != -1:
        return text[:last_underscore_index]
    else:
        # 如果没有下划线，返回原始字符串
        return text
