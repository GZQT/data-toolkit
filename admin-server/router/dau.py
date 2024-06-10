import io
from datetime import datetime
from typing import Union, List

import pandas as pd
from fastapi import APIRouter, Depends, Query, UploadFile, HTTPException
from fastapi_pagination import Page, add_pagination
from fastapi_pagination.ext.sqlalchemy import paginate
from sqlalchemy import select
from sqlalchemy.orm import Session

from dependency import get_db
from dto.dau import DauSearchResponse, DauSearchRequest
from schema.dau import DauConfig
from service.dau import import_dau_config

router = APIRouter(
    prefix="/dau",
    tags=["dau"],
)


@router.get("")
def search(param: DauSearchRequest = Depends(), db: Session = Depends(get_db)) -> Page[DauSearchResponse]:
    s = select(DauConfig)
    if param is None:
        return paginate(db, s.order_by(DauConfig.id.desc()))
    if param.name and param.name != '':
        s = s.where(DauConfig.name.ilike(f"%{param.name}%"))
    if param.bridge and param.bridge != '':
        s = s.where(DauConfig.bridge.ilike(f"%{param.bridge}%"))
    if param.collection_station_no and param.collection_station_no != '':
        s = s.where(DauConfig.collection_station_no.ilike(f"%{param.collection_station_no}%"))
    if param.collection_device_no and param.collection_device_no != '':
        s = s.where(DauConfig.collection_device_no.ilike(f"%{param.collection_device_no}%"))
    if param.ip_address and param.ip_address != '':
        s = s.where(DauConfig.ip_address.ilike(f"%{param.ip_address}%"))
    if param.sample_rate and param.sample_rate != '':
        s = s.where(DauConfig.sample_rate.ilike(f"%{param.sample_rate}%"))
    if param.physics_channel and param.physics_channel != '':
        s = s.where(DauConfig.physics_channel.ilike(f"%{param.physics_channel}%"))
    if param.install_no and param.install_no != '':
        s = s.where(DauConfig.install_no.ilike(f"%{param.install_no}%"))
    if param.transfer_no and param.transfer_no != '':
        s = s.where(DauConfig.transfer_no.ilike(f"%{param.transfer_no}%"))
    if param.monitor_project and param.monitor_project != '':
        s = s.where(DauConfig.monitor_project.ilike(f"%{param.monitor_project}%"))
    if param.device_type and param.device_type != '':
        s = s.where(DauConfig.device_type.ilike(f"%{param.device_type}%"))
    if param.manufacturer and param.manufacturer != '':
        s = s.where(DauConfig.manufacturer.ilike(f"%{param.manufacturer}%"))
    if param.specification and param.specification != '':
        s = s.where(DauConfig.specification.ilike(f"%{param.specification}%"))
    if param.device_no and param.device_no != '':
        s = s.where(DauConfig.device_no.ilike(f"%{param.device_no}%"))
    if param.install_location and param.install_location != '':
        s = s.where(DauConfig.install_location.ilike(f"%{param.install_location}%"))
    if param.direction and param.direction != '':
        s = s.where(DauConfig.direction.ilike(f"%{param.direction}%"))
    return paginate(db, s.order_by(DauConfig.id.desc()))


@router.post("/import/{bridge}", status_code=201)
async def import_dau(bridge: str, files: List[UploadFile], db: Session = Depends(get_db)):
    count = db.query(DauConfig).where(DauConfig.name.ilike(bridge)).count()
    if count > 0:
        raise HTTPException(status_code=400, detail=f"已经存在当前桥梁的数据了，无需再进行添加")
    dataframes = []
    for file in files:
        # 检查文件扩展名是否为 Excel 文件
        if not file.filename.endswith(('.xlsx', '.xls')):
            raise HTTPException(status_code=400, detail=f"文件 {file.filename} 并不是一个 Excel 文件")
        # 读取上传的文件内容
        contents = await file.read()
        try:
            # 使用 Pandas 读取 Excel 文件
            df = pd.read_excel(io.BytesIO(contents))
            dataframes.append(df)
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"读取 excel 文件失败 {file.filename} {e}")
    # 合并所有 DataFrame
    if dataframes:
        combined_df = pd.concat(dataframes, ignore_index=True).ffill()
    else:
        raise HTTPException(status_code=400, detail="文件合并失败，请重新尝试或者单个文件进行导入")
    import_dau_config(bridge, bridge, combined_df, db)


@router.post("", status_code=201)
def create_dau(request: DauSearchRequest, db: Session = Depends(get_db)):
    dau = request.to_orm()
    dau.created_date = datetime.now()
    db.add(dau)
    db.commit()


@router.put("/{id}", status_code=204)
def update_dau(id: int, request: DauSearchRequest, db: Session = Depends(get_db)):
    data = request.__dict__
    data["updated_date"] = datetime.now()
    db.query(DauConfig).filter_by(id=id).update(data)
    db.commit()


@router.delete("/{id}", status_code=204)
def delete_dau(id: int, db: Session = Depends(get_db)):
    db.query(DauConfig).filter_by(id=id).delete()
    db.commit()


add_pagination(router)
