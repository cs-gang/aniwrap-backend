FROM python:3.12-slim
COPY --from=ghcr.io/astral-sh/uv:0.7.14 /uv /uvx /bin/

WORKDIR /app
COPY . .
RUN uv sync --frozen --no-cache

CMD ["/app/.venv/bin/fastapi", "run", "aniwrap/app.py", "--port", "8000"] 