import argparse
import os

import uvicorn
from alembic import command
from alembic.config import Config
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

import database
from constant import ROOT_DIRECTORY, CUSTOM_LOGGING_CONFIG
from router import generator, task, health

app = FastAPI(
    title="Data Toolkit",
    version="0.0.1",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

home_dir = os.path.expanduser('~')

app.include_router(generator.router)
app.include_router(task.router)
app.include_router(health.router)

if __name__ == "__main__":
    if not os.path.exists(ROOT_DIRECTORY):
        os.makedirs(ROOT_DIRECTORY)
    database.Base.metadata.create_all(bind=database.engine)

    alembic_cfg = Config("alembic.ini")
    alembic_cfg.set_main_option("sqlalchemy.url", database.SQLALCHEMY_DATABASE_URL)
    command.upgrade(alembic_cfg, "head")

    parser = argparse.ArgumentParser(description='启动 web 后端服务', formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('--host', '-H', help='监听的主机地址', default="127.0.0.1", type=str)
    parser.add_argument('--port', '-P', help='监听的主机端口', default=18764, type=int)
    parser.add_argument('--reload', '-R', help='是否重新加载', default=False, type=bool)
    args = parser.parse_args()

    uvicorn.run(app, host=args.host, port=args.port, log_config=CUSTOM_LOGGING_CONFIG)
