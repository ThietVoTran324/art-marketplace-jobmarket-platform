import httpx
from app.logger import logger

httpx_client = None


async def init_httpx_client():
    global httpx_client
    try:
        httpx_client = httpx.AsyncClient()
        logger.info("✅ Httpx client initialization")

    except Exception as e:
        logger.error(f"❌ Error initializing Httpx client: {str(e)}")
        raise e


def get_httpx_client():
    if httpx_client is None:
        logger.error("Httpx client is not initialized!")
        raise RuntimeError("Httpx client is not initialized!")
    return httpx_client


async def close_httpx_client():
    global httpx_client
    if httpx_client:
        try:
            await httpx_client.aclose()
            logger.info("Httpx client closed")
        except Exception as e:
            logger.error(f"❌ Error closing Httpx client: {str(e)}")
