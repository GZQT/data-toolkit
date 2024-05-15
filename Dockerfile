# 使用带有 Node.js 的官方 Python 镜像作为基础镜像
FROM python:3.12

# 更新包管理器并安装必要的依赖
RUN apt-get update && apt-get install -y \
  curl \
  gnupg \
  && rm -rf /var/lib/apt/lists/*

# 安装 Node.js 20
RUN curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
  && apt-get install -y nodejs \
  && npm install -g npm@latest

# 安装 Poetry
RUN curl -sSL https://install.python-poetry.org | python3 - \
  && pip install pyinstaller

# 设置 Poetry 的路径
ENV PATH="/root/.local/bin:$PATH"

COPY server/pyproject.toml server/poetry.lock /app/server/
COPY client/package.json client/package-lock.json /app/client/

# 安装 server 依赖
RUN cd /app/server && poetry install

# 安装 client 依赖
RUN cd /app/client && npm install

# 设置工作目录
WORKDIR /app

# 设置默认命令
CMD ["tail", "-f", "/dev/null"]
