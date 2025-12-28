FROM wodby/python:3.14-dev@sha256:5bdb5fefbdd9cd231f015c82a5e8377ac2e0ba947d1e789b719fd72b79ea111b AS build

ARG ENVIRONMENT=production

RUN --mount=type=cache,id=pip-cache,uid=1000,gid=1000,target=/home/wodby/.cache/pip/ \
    --mount=type=cache,id=poetry-cache,uid=1000,gid=1000,target=/home/wodby/.cache/pypoetry/ \
    pip install --upgrade pip && \
    pip install poetry && \
    poetry config virtualenvs.create false

ADD ./pyproject.toml ./poetry.lock ./LICENSE ./

RUN --mount=type=cache,id=poetry-cache,uid=1000,gid=1000,target=/home/wodby/.cache/pypoetry/ \
    if [ "$ENVIRONMENT" = "development" ]; then \
        poetry install; \
    else \
        poetry install --without dev; \
    fi


FROM wodby/python:3.14@sha256:248546885341200cbe957253e85270f9f2ab6b510023474f895b363e2a513fe9 AS runtime

USER root

RUN apk add --no-cache \
    pango \
    fontconfig \
    ttf-dejavu

USER wodby

COPY LICENSE ./

ENV GUNICORN_APP=main.wsgi:application

COPY --from=build /home/wodby/.local/lib/python3.14/site-packages/ /home/wodby/.local/lib/python3.14/site-packages/
COPY --from=build /home/wodby/.local/bin/ /home/wodby/.local/bin/

COPY ./src ./
