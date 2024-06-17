import os
from pathlib import Path

import uvicorn
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

import database
from constant import CUSTOM_LOGGING_CONFIG, ROOT_DIRECTORY, server_log, server_access_log
from router import dau, health

app = FastAPI(
    title="admin server",
    version="0.0.1",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(dau.router)
app.include_router(health.router)

if __name__ == '__main__':
    if not os.path.exists(ROOT_DIRECTORY):
        Path(ROOT_DIRECTORY).mkdir(parents=True, exist_ok=True)
    database.Base.metadata.create_all(bind=database.engine)
    uvicorn.run(app, host="0.0.0.0", port=8881, log_config=CUSTOM_LOGGING_CONFIG)
