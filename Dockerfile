FROM python:alpine3.10

WORKDIR /app

COPY aninas ./aninas
COPY pyproject.toml .

RUN apk update && apk add git gcc musl-dev python3-dev linux-headers
RUN pip install .

CMD ["python3", "-m" "aninas"]