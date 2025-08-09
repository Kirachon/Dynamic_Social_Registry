import asyncio
import os
from aiokafka import AIOKafkaProducer, AIOKafkaConsumer
from .events import kafka_bootstrap
from .otel_kafka import tracer, build_headers, context_from_traceparent
from .trace import current_traceparent

_producer = None

async def get_producer() -> AIOKafkaProducer:
    global _producer
    if _producer is None:
        _producer = AIOKafkaProducer(bootstrap_servers=kafka_bootstrap())
        await _producer.start()
    return _producer

async def stop_producer():
    global _producer
    if _producer:
        await _producer.stop()
        _producer = None

async def send_event(producer: AIOKafkaProducer, topic: str, payload: bytes, traceparent: str | None):
    headers = build_headers(traceparent)
    with tracer.start_as_current_span("kafka.produce", attributes={"messaging.system":"kafka","messaging.destination":topic}):
        await producer.send_and_wait(topic, payload, headers=headers)

async def make_consumer(*topics: str, group_id: str) -> AIOKafkaConsumer:
    consumer = AIOKafkaConsumer(*topics, bootstrap_servers=kafka_bootstrap(), group_id=group_id, enable_auto_commit=False)
    await consumer.start()
    return consumer

async def next_event(consumer: AIOKafkaConsumer):
    msg = await consumer.getone()
    # extract trace context
    tp = None
    if msg.headers:
        for k, v in msg.headers:
            if k == b"traceparent":
                tp = v.decode("utf-8")
                break
    ctx = context_from_traceparent(tp)
    span = tracer.start_span("kafka.consume", context=ctx, attributes={"messaging.system":"kafka","messaging.destination":msg.topic})
    span.end()
    return msg

