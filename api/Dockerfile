FROM python:3.14.3-alpine

WORKDIR /app

RUN apk update \
    && apk add --no-cache --virtual .build-dependencies build-base libffi-dev libxslt-dev musl-dev \
    && apk add --no-cache --virtual .runtime-dependencies curl git jq libxslt make

COPY . /app/

RUN --mount=from=ghcr.io/astral-sh/uv,source=/uv,target=/bin/uv \
    --mount=type=cache,target=/root/.cache/uv \
    uv export --all-extras --locked > requirements.txt \
    && uv pip install --system -r requirements.txt \
    && uv pip install --system -e . \
    && apk del .build-dependencies
