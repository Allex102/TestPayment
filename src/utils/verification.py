import secrets
from typing import Annotated

from fastapi import Header, HTTPException, status

from src.config import settings

async def verify_api_key(
    api_key: Annotated[str | None, Header(alias="X-API-Key")] = None,
) -> None:
    if (
        not api_key
        or not secrets.compare_digest(api_key, settings.API_KEY)
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key",
        )