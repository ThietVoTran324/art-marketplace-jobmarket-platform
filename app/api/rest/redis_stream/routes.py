import asyncio

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query

from app.config import settings
from redis import asyncio as aioredis
from redis.exceptions import RedisError

router = APIRouter(prefix="/redis-stream", tags=["redis-stream"])


async def get_redis() -> aioredis.Redis:
    return await aioredis.from_url(settings.REDIS_URL_CELERY_BROKER, decode_responses=True)


@router.post("/group/create", summary="Create a Redis Stream consumer group")
async def create_consumer_group(
    stream_name: str = Query("mystream"),
    group_name: str = Query("mygroup"),
    redis: aioredis.Redis = Depends(get_redis),
):
    try:
        await redis.xgroup_create(stream_name, group_name, id="0", mkstream=True)
        return {"message": f"Group '{group_name}' successfully created in stream '{stream_name}'."}
    except RedisError as e:
        if "BUSYGROUP" in str(e):
            raise HTTPException(
                status_code=400, detail=f"Group '{group_name}' already exists."
            )
        raise HTTPException(status_code=500, detail="Error creating group.")


@router.post("/stream/add-message", summary="Add a message to a Redis Stream")
async def add_message_to_stream(
    message: str, stream_name: str = Query("mystream"), redis: aioredis.Redis = Depends(get_redis)
):
    message_id = await redis.xadd(stream_name, {"text": message})
    return {
        "message": f"Message '{message}' added to stream '{stream_name}' with ID {message_id}."
    }


async def stream_worker(stream_name: str, group_name: str, consumer_name: str):
    redis = await get_redis()
    try:
        while True:
            messages = await redis.xreadgroup(
                groupname=group_name,
                consumername=consumer_name,
                streams={stream_name: ">"},
                count=1,
                block=5000,
            )
            if messages:
                for stream, entries in messages:
                    for message_id, data in entries:
                        print(f"[{consumer_name}] Received message: {data} with ID: {message_id}")
                        await redis.xack(stream_name, group_name, message_id)
    except asyncio.CancelledError:
        print(f"[{consumer_name}] Worker stopped.")


@router.post("/stream/consume", summary="Start a stream worker via BackgroundTasks")
async def consume_stream(
    background_tasks: BackgroundTasks,
    consumer_name: str = Query("worker-1"),
    stream_name: str = Query("mystream"),
    group_name: str = Query("mygroup"),
):
    background_tasks.add_task(stream_worker, stream_name, group_name, consumer_name)
    return {
        "message": (
            f"Worker '{consumer_name}' started in the background "
            f"for stream '{stream_name}' and group '{group_name}'."
        )
    }


@router.get("/stream/messages", summary="List all messages from a stream")
async def get_stream_messages(
    stream_name: str = Query("mystream"),
    count: int = Query(10, description="Maximum number of messages to return"),
    redis: aioredis.Redis = Depends(get_redis),
):
    try:
        messages = await redis.xrange(stream_name, count=count)
        formatted_messages = [{"id": message_id, "data": data} for message_id, data in messages]
        return {"stream": stream_name, "messages": formatted_messages}
    except RedisError as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving messages: {str(e)}")
