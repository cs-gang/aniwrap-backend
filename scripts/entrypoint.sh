#!/bin/bash

uv run alembic upgrade head &&
if [[ $ANIWRAP_DEBUG == "true" ]]; then
    uv run fastapi dev aniwrap/app.py --host 0.0.0.0 --port 8000
else
    uv run fastapi run aniwrap/app.py --port 8000
fi
