from typing import Annotated

import httpx
from fastapi import Depends

from app.core.http import http_client
from app.modules.facebook.client import FacebookClient


def get_http_client() -> httpx.AsyncClient:
    return http_client


def get_facebook_client(
    http: Annotated[httpx.AsyncClient, Depends(get_http_client)],
) -> FacebookClient:
    return FacebookClient(http)


FacebookClientDep = Annotated[
    FacebookClient,
    Depends(get_facebook_client),
]
