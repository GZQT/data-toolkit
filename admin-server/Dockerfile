FROM python:3.12-alpine

RUN pip install poetry
WORKDIR /app
COPY . .
RUN poetry config virtualenvs.create false && \
    poetry install --no-root
EXPOSE 8881

CMD ["poetry", "run", "python", "application.py"]
