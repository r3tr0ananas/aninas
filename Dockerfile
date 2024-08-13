FROM python:3.10-slim-bookworm

WORKDIR /app

COPY aninas ./aninas
COPY pyproject.toml .
COPY main.py .

RUN apt-get update && apt-get install -y git gcc
RUN pip install .

CMD ["python3", "main.py"]
