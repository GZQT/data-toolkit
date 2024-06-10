from fastapi import HTTPException
from pandas import DataFrame, Series
from sqlalchemy.orm import Session

from schema.dau import DauConfig


def import_dau_config(name: str, bridge: str, data: DataFrame | Series, db: Session):
    records = []
    for index, row in data.iterrows():
        record = DauConfig(
            name=name,
            bridge=bridge,
            collection_station_no=row.iloc[0] if len(row) > 0 else None,
            collection_device_no=row.iloc[1] if len(row) > 1 else None,
            ip_address=row.iloc[2] if len(row) > 2 else None,
            sample_rate=row.iloc[3] if len(row) > 3 else None,
            physics_channel=row.iloc[4] if len(row) > 4 else None,
            install_no=row.iloc[5] if len(row) > 5 else None,
            transfer_no=row.iloc[6] if len(row) > 6 else None,
            monitor_project=row.iloc[7] if len(row) > 7 else None,
            device_type=row.iloc[8] if len(row) > 8 else None,
            manufacturer=row.iloc[9] if len(row) > 9 else None,
            specification=row.iloc[10] if len(row) > 10 else None,
            device_no=row.iloc[11] if len(row) > 11 else None,
            install_location=row.iloc[12] if len(row) > 12 else None,
            direction=row.iloc[13] if len(row) > 13 else None,
        )
        records.append(record)
    db.bulk_save_objects(records)
    db.commit()
