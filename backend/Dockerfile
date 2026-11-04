FROM python:3.15.2-alpine

WORKDIR /app

RUN apk update \
    && apk add --no-cache --virtual .build-dependencies build-base libffi-dev libxslt-dev musl-dev postgresql-dev \
    && apk add --no-cache --virtual .runtime-dependencies curl git jq libpq libxslt make

COPY pyproject.toml uv.lock /app/

RUN --mount=from=ghcr.io/astral-sh/uv,source=/uv,target=/bin/uv \
    --mount=type=cache,target=/root/.cache/uv \
    mkdir -p /app/backend/src/maps \
    && touch /app/backend/src/maps/__init__.py \
    && touch /app/backend/README.md \
    && uv export --all-extras --locked > requirements.txt \
    && uv pip install --system -r requirements.txt \
    && uv pip install --system -e . \
    && apk del .build-dependencies

COPY backend /app/backend/

WORKDIR /app/backend
