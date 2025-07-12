from typing import Annotated, Literal

from fastapi import APIRouter, Path

router = APIRouter(prefix="/wrapped")


Provider = Literal["mal", "anilist"]


@router.get("/{provider}/{username}")
async def get_wrapped(
    provider: Annotated[Provider, Path(description="The anime tracking provider")],
    username: Annotated[
        str, Path(description="The user's username on the specified platform")
    ],
): ...
