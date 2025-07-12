from contextlib import asynccontextmanager

import aiohttp
from fastapi import FastAPI


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.http = aiohttp.ClientSession()
    yield
    await app.state.http.close()


app = FastAPI(lifespan=lifespan)


@app.get("/ping")
def ping():
    return {"message": "pong!"}
