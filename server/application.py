import argparse
import os
import matplotlib

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
matplotlib.use('Agg')


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='启动 web 后端服务', formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('--host', '-H', help='监听的主机地址', default="127.0.0.1", type=str)
    parser.add_argument('--port', '-P', help='监听的主机端口', default=18764, type=int)
    parser.add_argument('--reload', '-R', help='是否重新加载', default=False, type=bool)
    parser.add_argument('--path', '-p', help='可执行文件路径', default=os.path.curdir, type=str)
    args = parser.parse_args()

    if not os.path.exists(ROOT_DIRECTORY):
        os.makedirs(ROOT_DIRECTORY)
    alembic_cfg = Config(os.path.abspath(os.path.join(args.path, "alembic.ini")))
    alembic_cfg.set_main_option("sqlalchemy.url", database.SQLALCHEMY_DATABASE_URL)
    alembic_cfg.set_main_option("script_location",
                                os.path.abspath(os.path.join(args.path, "alembic")))
    if os.path.exists(os.path.join(ROOT_DIRECTORY, 'sql_app.db')):
        command.upgrade(alembic_cfg, "15b5635b3f66")
    else:
        database.Base.metadata.create_all(bind=database.engine)
        command.stamp(alembic_cfg, "15b5635b3f66")
    uvicorn.run(app, host=args.host, port=args.port, log_config=CUSTOM_LOGGING_CONFIG)
