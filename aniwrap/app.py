from contextlib import asynccontextmanager

import aiohttp
from fastapi import FastAPI

from aniwrap.api.watch_history import router as watch_history_router
from aniwrap.api.wrapped import router as wrapped_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.http = aiohttp.ClientSession()
    yield
    await app.state.http.close()


app = FastAPI(lifespan=lifespan)

app.include_router(watch_history_router)
app.include_router(wrapped_router)


@app.get("/ping")
def ping():
    return {"message": "pong!"}
