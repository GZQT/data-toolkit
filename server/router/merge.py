import os
from typing import Optional, List

import pandas as pd
import asyncio
from fastapi import APIRouter, HTTPException

from utils import get_time_column, remove_last_underscore, get_file_now_date
from constant import logger, ROOT_DIRECTORY
from dto.merge import MergeRequest, MergeFiles

router = APIRouter(
    prefix="/merge",
    tags=["merge"],
)


@router.post("", status_code=200)
async def merge(request: MergeRequest):
    # 提取请求中的参数
    files = request.files
    base = request.base
    config = request.config

    # 读取并处理基准文件
    base_df = await read_and_process_csv(base.file_path, [base.column], is_base=True)
    if base_df is None:
        raise HTTPException(status_code=400, detail="上传的基准点表格不存在时间列 time/col0. ")

    # 并发处理多个文件
    file_dataframes = await asyncio.gather(
        *[read_and_process_csv(file.file_path, file.select_columns) for file in files if file.select_columns]
    )

    # 合并所有文件
    for df in file_dataframes:
        if df is not None:
            base_df = base_df.join(df, how='outer')

    # 根据配置清理数据
    if config:
        if config.remove_base_null:
            base_df.dropna(subset=[base_df.columns[0]], inplace=True)  # 基准列的空值去除
        if config.remove_null:
            base_df.dropna(how='any', inplace=True)

    # 导出合并后的数据
    export_dir = os.path.join(ROOT_DIRECTORY, '数据合并')
    os.makedirs(export_dir, exist_ok=True)
    output_file_path = os.path.join(export_dir, f'{get_file_now_date()}_merged_output.csv')
    base_df.to_csv(output_file_path)
    logger.info(f"导出表格数据完成，路径: {output_file_path}")

    return {"message": "合并成功", "output_file": output_file_path}


async def read_and_process_csv(file_path: str, columns: List[str], is_base: bool = False) -> Optional[pd.DataFrame]:
    """
    读取并处理 CSV 文件，提取时间列，格式化时间并返回 DataFrame。
    :param file_path: CSV 文件路径
    :param columns: 要读取的列名
    :param is_base: 是否是基准文件，如果是基准文件需要重命名列
    :return: 处理后的 DataFrame 或 None
    """
    if not os.path.exists(file_path):
        logger.warning(f"表格 {file_path} 不存在")
        return None

    # 读取表头以检查时间列
    df = pd.read_csv(file_path, nrows=0)
    time_col = get_time_column(df)
    if time_col is None:
        logger.warning(f"表格 {file_path} 不存在时间列 time/col0. ")
        return None

    # 读取指定列数据并处理时间列
    df = pd.read_csv(file_path, usecols=[time_col] + columns)
    df[time_col] = pd.to_datetime(df[time_col], format='%Y-%m-%d-%H-%M-%S.%f', errors='coerce')
    df.dropna(subset=[time_col], inplace=True)  # 去除无效时间的行
    df[time_col] = df[time_col].dt.strftime('%Y-%m-%d-%H-%M-%S')
    df.set_index(time_col, inplace=True)

    # 重命名列，如果是基准文件或其他文件
    if is_base:
        df.columns = [f"base_{os.path.basename(file_path).replace('.csv', '')}_{columns[0]}"]
    else:
        df.columns = [f"{remove_last_underscore(os.path.basename(file_path).replace('.csv', ''))}_{col}" for col in columns]

    return df
