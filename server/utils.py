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
