FROM python:3.11.14-alpine

WORKDIR /app

COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/

RUN apk update \
    && apk add --no-cache --virtual .build-dependencies build-base libffi-dev libxslt-dev musl-dev \
    && apk add --no-cache --virtual .runtime-dependencies curl git jq libxslt make

COPY pyproject.toml uv.lock /app/

RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --no-dev --frozen \
    && apk del .build-dependencies

COPY . /app/
