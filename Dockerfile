FROM python:alpine

WORKDIR /app

COPY aninas ./aninas
COPY pyproject.toml .

RUN apk update && apk add git
RUN pip install .

CMD ["python3", "-m" "aninas"]
