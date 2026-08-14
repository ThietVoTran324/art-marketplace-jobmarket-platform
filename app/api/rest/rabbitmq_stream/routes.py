import aio_pika
from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse

from app.rabbitmq.app import get_rabbitmq_connection_and_channel

router = APIRouter(prefix="/rabbitmq-stream", tags=["rabbitmq-stream"])


@router.post("/send")
async def send_message(message: str):
    try:
        connection, channel = await get_rabbitmq_connection_and_channel()

        await channel.default_exchange.publish(
            aio_pika.Message(body=message.encode()), routing_key="messages"
        )

        return {"status": "message sent"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/read")
async def read_messages():
    try:
        connection, channel = await get_rabbitmq_connection_and_channel()

        queue = await channel.declare_queue("messages", durable=True)
        messages = []

        message_limit = 10
        count = 0

        async for message in queue:
            if count >= message_limit:
                break
            async with message.process():
                messages.append(message.body.decode())
                count += 1

        return JSONResponse(content={"messages": messages})

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
