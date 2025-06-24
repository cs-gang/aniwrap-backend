# aniwrap-backend
Backend server for Anime Wrapped

## Dev Setup

Install dependencies with `uv`:
```
uv sync --frozen
```

Install pre-commit hooks:
```
uv run pre-commit install
```

Run the server:
```
uv run fastapi dev aniwrap/app.py
```
