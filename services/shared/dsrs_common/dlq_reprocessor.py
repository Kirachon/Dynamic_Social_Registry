import asyncio
import json
from aiokafka import AIOKafkaConsumer, AIOKafkaProducer
from .events import Event, topic_for, kafka_bootstrap
from .kafka import make_consumer, get_producer, next_event, send_event

async def dlq_reprocess_loop(group_id: str = "dlq-reprocessor", retry_delay: float = 2.0, max_retries: int = 3):
    # Subscribe to all known DLQs
    topics = [
        "registry.household.dlq",
        "eligibility.assessed.dlq",
        "payment.events.dlq",
    ]
    consumer = await make_consumer(*topics, group_id=group_id)
    producer = await get_producer()
    try:
        while True:
            msg = await next_event(consumer)
            evt = Event.from_json(msg.value.decode("utf-8"))
            orig = evt.data.get("original", {})
            original_type = orig.get("type") or evt.type.replace(".dead","")
            original_topic = topic_for(original_type)
            # Simple bounded retry loop; in practice include retry count in headers/body
            ok = False
            for i in range(max_retries):
                try:
                    await send_event(producer, original_topic, json.dumps(orig).encode("utf-8"), evt.traceparent)
                    ok = True
                    break
                except Exception:
                    await asyncio.sleep(retry_delay * (2 ** i))
            if ok:
                await consumer.commit()
            else:
                # Leave in DLQ for manual intervention
                await consumer.commit()
    finally:
        await consumer.stop()

