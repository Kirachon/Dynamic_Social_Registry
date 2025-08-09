import asyncio
import os
from aiokafka import AIOKafkaProducer, AIOKafkaConsumer
from .events import kafka_bootstrap

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

async def make_consumer(*topics: str, group_id: str) -> AIOKafkaConsumer:
    consumer = AIOKafkaConsumer(*topics, bootstrap_servers=kafka_bootstrap(), group_id=group_id, enable_auto_commit=False)
    await consumer.start()
    return consumer

