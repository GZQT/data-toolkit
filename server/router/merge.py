import os

import pandas as pd
from fastapi import APIRouter, HTTPException

import utils
from constant import logger, ROOT_DIRECTORY
from dto.merge import MergeRequest

router = APIRouter(
    prefix="/merge",
    tags=["merge"],
)


@router.post("", status_code=200)
async def merge(request: MergeRequest):
    files = request.files
    base = request.base

    base_df = pd.read_csv(base.file_path, nrows=0)
    time_col = utils.get_time_column(base_df)
    if time_col is None:
        logger.warning("上传的基准点表格不存在时间列 time/col0. ")
        raise HTTPException(status_code=400, detail="上传的基准点表格不存在时间列 time/col0. ")

    base_df = pd.read_csv(base.file_path, usecols=[time_col, base.column])
    base_df[time_col] = pd.to_datetime(base_df[time_col], format='%Y-%m-%d-%H-%M-%S.%f')
    base_df[time_col] = base_df[time_col].dt.strftime('%Y-%m-%d-%H-%M-%S')
    base_df = base_df.rename(columns={
        base.column: f"base_{os.path.basename(base.file_path).replace('.csv', '')}_{base.column}"
    }).set_index(time_col)

    for file in files:
        if len(file.select_columns) == 0:
            continue
        file_path = file.file_path
        logger.info(f"开始处理表格 {file_path}")
        if not os.path.exists(file_path):
            logger.warning(f"表格 {file_path} 不存在")
            continue
        df = pd.read_csv(file_path, nrows=0)
        time_col = utils.get_time_column(df)
        if time_col is None:
            logger.warning(f"上传的表格 {file_path} 不存在时间列 time/col0. ")
            continue
        df = pd.read_csv(file_path, usecols=[time_col] + file.select_columns)
        df[time_col] = pd.to_datetime(df[time_col], format='%Y-%m-%d-%H-%M-%S.%f')
        df[time_col] = df[time_col].dt.strftime('%Y-%m-%d-%H-%M-%S')
        df = df.set_index(time_col)
        # 处理列名重复问题
        df.columns = [f"{os.path.basename(file_path).replace('.csv', '')}_{col}" for col in df.columns]
        base_df = base_df.join(df, how='outer')

    # 导出合并后的数据到指定的 CSV 文件
    logger.info(f"开始导出表格数据")
    merge_dir = os.path.join(ROOT_DIRECTORY, '数据合并')
    if not os.path.exists(merge_dir):
        os.makedirs(merge_dir)
    base_df.to_csv(os.path.join(merge_dir, f'{utils.get_file_now_date()}_merged_output.csv'))
    logger.info(f"导出表格数据完成")
