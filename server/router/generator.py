import datetime
from fastapi import APIRouter, Depends, BackgroundTasks, HTTPException
from sqlalchemy.orm import Session
from starlette.responses import StreamingResponse

from constant import logger
from dependency import get_db
from dto.generator import GeneratorResponse, GeneratorCreateRequest, \
    TaskGeneratorStartRequest, GeneratorAllResponse, BarChartGeneratorStartRequest, PreviewImageRequest
from schema.task import TaskGenerator
from service.chart_generator import generate_chart, generate_bar_chart
from service.chart_preview import preview_line_chart
from utils import generate_data

router = APIRouter(
    prefix="/task",
    tags=["task", "generator"],
)


@router.get("/{task_id}/generator", response_model=list[GeneratorResponse])
def get_generator(task_id: int, db: Session = Depends(get_db)):
    return db.query(TaskGenerator).filter_by(task_id=task_id).order_by(TaskGenerator.id.desc()).all()


@router.post("/{task_id}/generator", response_model=GeneratorResponse)
def add_generator(task_id: int, generator: GeneratorCreateRequest, db: Session = Depends(get_db)):
    entity = TaskGenerator(**generator.dict(),
                           created_date=datetime.datetime.now(),
                           updated_date=datetime.datetime.now(),
                           task_id=task_id)
    db.add(entity)
    db.commit()
    db.refresh(entity)
    return entity


@router.put("/{task_id}/generator/{generator_id}", status_code=204)
def update_generator(task_id: int, generator_id: int, generator: GeneratorCreateRequest, db: Session = Depends(get_db)):
    (db.query(TaskGenerator).filter_by(id=generator_id).
     update({TaskGenerator.name: generator.name,
             TaskGenerator.files: generator.files,
             TaskGenerator.updated_date: datetime.datetime.now()}))
    db.commit()


@router.put("/{task_id}/generator/{generator_id}/clearOutput", status_code=204)
def update_generator(task_id: int, generator_id: int, db: Session = Depends(get_db)):
    (db.query(TaskGenerator).filter_by(id=generator_id).
     update({TaskGenerator.output: '', TaskGenerator.updated_date: datetime.datetime.now()}))
    db.commit()


@router.get("/{task_id}/generator/{generator_id}", response_model=GeneratorAllResponse)
def get_generator(task_id: int, generator_id: int, db: Session = Depends(get_db)):
    return db.query(TaskGenerator).filter_by(id=generator_id, task_id=task_id).first()


@router.delete("/{task_id}/generator/{generator_id}", status_code=204)
def update_generator(generator_id: int, db: Session = Depends(get_db)):
    db.query(TaskGenerator).filter_by(id=generator_id).delete()
    db.commit()


@router.post("/{task_id}/generator/{generator_id}", status_code=204)
def start_generator(task_id: int, generator_id: int,
                    request: TaskGeneratorStartRequest,
                    background_tasks: BackgroundTasks,
                    db: Session = Depends(get_db)):
    generator: TaskGenerator = db.query(TaskGenerator).filter_by(id=generator_id).scalar()
    if generator is None or generator.files is None:
        return
    background_tasks.add_task(generate_chart, generator, request, db)
    logger.info(f"已添加柱状图图生成任务，参数为 {generator_id} {request.__dict__}")


@router.post("/{task_id}/generate/barChart", status_code=204)
def start_bar_chart(task_id: int, request: BarChartGeneratorStartRequest,
                    background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    generators = db.query(TaskGenerator).filter(TaskGenerator.id.in_(request.generator_ids)).all()
    if len(generators) != len(request.generator_ids):
        raise HTTPException(status_code=400, detail="有一部分数据不存在，请刷新后尝试")
    background_tasks.add_task(generate_bar_chart, generators, request, db)
    logger.info(f"已添加柱状图图生成任务，参数为 {request.__dict__}")


@router.post("/image/preview/line")
def preview_line_image(request: PreviewImageRequest):
    data = generate_data('2024-01-01 00:00:00', '2024-03-31 23:59:59', request.chart_data_number, (0, 100))
    buffer = preview_line_chart(data, request)
    return StreamingResponse(buffer, media_type="image/png")
