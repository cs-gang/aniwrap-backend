"""Miscellaneous helper functions and stuff."""

from fastapi import Request
from aiohttp import ClientSession


def get_http_client(request: Request) -> ClientSession:
    return request.app.state.http
