FROM python:3.12-slim
COPY --from=ghcr.io/astral-sh/uv:0.7.14 /uv /uvx /bin/

WORKDIR /app
COPY . .
RUN uv sync --frozen --no-cache
RUN chmod +x scripts/entrypoint.sh

CMD ["./scripts/entrypoint.sh"]