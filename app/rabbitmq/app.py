import asyncio
import aio_pika

from app.config import settings
from app.logger import logger

rabbitmq_connection = None
rabbitmq_channel = None


async def init_rabbitmq():
    """Initialize RabbitMQ connection with retry logic."""
    global rabbitmq_connection, rabbitmq_channel
    max_retries = 5
    retry_delay = 2

    for attempt in range(max_retries):
        try:
            rabbitmq_connection = await asyncio.wait_for(
                aio_pika.connect_robust(settings.RABBITMQ_URL_BROKER),
                timeout=10.0,
            )
            rabbitmq_channel = await rabbitmq_connection.channel()
            logger.info("Successfully connected to RabbitMQ")
            return rabbitmq_connection, rabbitmq_channel
        except Exception as e:
            rabbitmq_connection = None
            rabbitmq_channel = None
            if attempt < max_retries - 1:
                logger.warning(
                    "RabbitMQ connection attempt %s/%s failed: %s. Retrying in %ss...",
                    attempt + 1,
                    max_retries,
                    e,
                    retry_delay,
                )
                await asyncio.sleep(retry_delay)
            else:
                logger.error(
                    "Error connecting to RabbitMQ after %s attempts: %s",
                    max_retries,
                    e,
                )
                return None, None


async def close_rabbitmq():
    """Close RabbitMQ connection and channel."""
    global rabbitmq_connection, rabbitmq_channel
    if rabbitmq_channel:
        try:
            await rabbitmq_channel.close()
            logger.info("RabbitMQ channel closed")
        except Exception as e:
            logger.error("Error closing RabbitMQ channel: %s", e)

    if rabbitmq_connection:
        try:
            await rabbitmq_connection.close()
            logger.info("RabbitMQ connection closed")
        except Exception as e:
            logger.error("Error closing RabbitMQ connection: %s", e)


async def get_rabbitmq_connection_and_channel():
    """Return the current RabbitMQ connection and channel."""
    global rabbitmq_connection, rabbitmq_channel
    if rabbitmq_connection is None or rabbitmq_channel is None:
        raise RuntimeError("RabbitMQ is not connected. Initialize the connection first.")
    return rabbitmq_connection, rabbitmq_channel
