
FROM python:3.14-slim
COPY --from=astral/uv:latest /uv /usr/local/bin/uv

# tells Python not to buffer stdout and stderr, so anything you print() is written out immediately
ENV PYTHONUNBUFFERED=1 \
    UV_CACHE_DIR=/tmp/uv-cache \
    UV_PROJECT_ENVIRONMENT=/todo-app/.venv \
    UVICORN_HOST=0.0.0.0 \
    UVICORN_PORT=8000

RUN useradd --no-create-home --shell /usr/sbin/nologin appuser

WORKDIR /todo-app

COPY --chown=appuser:appuser todo-app .

RUN uv sync --no-dev --no-install-project

USER appuser

CMD ["/todo-app/.venv/bin/uvicorn", "src.todo_app.main:app"]

