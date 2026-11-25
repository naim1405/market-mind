import httpx

http_client = httpx.AsyncClient(
    timeout=httpx.Timeout(10.0, connect=5.0),
    limits=httpx.Limits(
        max_connections=100,
        max_keepalive_connections=20,
    ),
)
