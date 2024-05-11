import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from dependency import get_db
from dto.task import TaskResponse, TaskCreateRequest, TaskFileResponse, TaskFileCreateRequest, \
    TaskFileUpdateRequest
from schema.task import Task, TaskFile

router = APIRouter(
    prefix="/task",
    tags=["task"],
)


@router.get("", response_model=list[TaskResponse])
def get_task(db: Session = Depends(get_db)):
    return db.query(Task).order_by(Task.id.desc()).all()


@router.post("", response_model=TaskResponse, status_code=201)
def add_task(task: TaskCreateRequest, db: Session = Depends(get_db)):
    entity = Task(name=task.name, files=[])
    db.add(entity)
    db.commit()
    db.refresh(entity)
    return entity


@router.put("/{task_id}", status_code=204)
def update_task_name(task_id: int, task: TaskCreateRequest, db: Session = Depends(get_db)):
    (db.query(Task).filter_by(id=task_id).
     update({Task.name: task.name, Task.updated_date: datetime.datetime.now()}))
    db.commit()


@router.delete("/{task_id}", status_code=204)
def remove_task_file(task_id: int, db: Session = Depends(get_db)):
    db.query(Task).filter_by(id=task_id).delete()
    db.commit()


@router.get("/{task_id}/file", response_model=list[TaskFileResponse])
def get_task_file(task_id: int, db: Session = Depends(get_db)):
    return db.query(TaskFile).filter_by(task_id=task_id). \
        order_by(TaskFile.id.desc()).all()


@router.post("/{task_id}/file", status_code=201)
def add_task_file(task_id: int, task_file: TaskFileCreateRequest, db: Session = Depends(get_db)):
    count = db.query(Task).filter_by(id=task_id).count()
    if count == 0:
        raise HTTPException(status_code=400, detail="关联的任务不存在，请重新选择任务后进行创建")
    entity_list = []
    for name in task_file.names:
        entity_list.append(TaskFile(name=name, task_id=task_id))
    db.add_all(entity_list)
    db.commit()


@router.put("/{task_id}/file/{task_file_id}", status_code=204)
def update_task_file(task_id: int, task_file_id: int, task_file: TaskFileUpdateRequest, db: Session = Depends(get_db)):
    (db.query(TaskFile).filter_by(id=task_file_id, task_id=task_id).
     update({TaskFile.name: task_file.name, TaskFile.updated_date: datetime.datetime.now()}))
    db.commit()


@router.delete("/{task_id}/file/{task_file_id}", status_code=204)
def remove_task_file(task_id: int, task_file_id: int, db: Session = Depends(get_db)):
    db.query(TaskFile).filter_by(id=task_file_id, task_id=task_id).delete()
    db.commit()
