import pandas as pd
import numpy as np

if __name__ == '__main__':
    # 读取CSV文件
    df = pd.read_csv(
        "C:\\Users\\zyue\\PycharmProjects\\data-crawl\\data_chart\\pu_an_no_1\\普安1号特大桥数据\\data_dau_pa1_1_通用采集仪_20240229.csv")

    # 忽略 'id' 列和任何以 'Unnamed' 开头的列
    df = df.loc[:, ~df.columns.str.contains('^Unnamed|^id')]

    # 确定时间列，优先考虑 'time'，如果不存在则使用 'col0'
    time_column = 'time' if 'time' in df.columns else 'col0'

    # 确保时间列存在
    if time_column not in df.columns:
        raise ValueError("No valid time column found. Expected 'time' or 'col0'.")

    data_frames = {}

    # 遍历所有列，除了时间列
    for column in df.columns:
        if column == time_column:
            continue
        data_frames[column] = pd.DataFrame({
            'time': df[time_column],
            'data': df[column]
        })

    # 输出字典中的一个示例DataFrame来验证
    for key, value in data_frames.items():
        print(f"DataFrame for column {key}:")
        print(value.head(), "\n")  # 打印每个DataFrame的头部几行
