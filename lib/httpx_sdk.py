import httpx


class HttpxSDK:
    async_client: httpx.AsyncClient | None = None

    @classmethod
    async def close_async_client(cls) -> None:
        async_client = cls.async_client

        if async_client:
            if not async_client.is_closed:
                # Close `async_client` if it hasn't already
                await async_client.aclose()

            # Unset the async client so that it can be set again if necessary
            cls.async_client = None

    @classmethod
    def get_async_client(cls) -> httpx.AsyncClient:
        async_client = cls.async_client

        if async_client is None:
            async_client = httpx.AsyncClient()
            cls.async_client = async_client
        return async_client
