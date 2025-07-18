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

Before running the server, you will need to set up a few environment variables.
See the `.env.example` file for a list of required variables.

Run the server with Docker:
You can either run the latest released version, by pulling the image from GHCR.
For an example, see the `compose.yml` file.

To run the server in development:
```
docker compose -f dev.compose.yml up
```
