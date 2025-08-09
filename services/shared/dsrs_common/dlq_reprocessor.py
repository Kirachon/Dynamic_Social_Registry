import asyncio
import json
import time
from typing import Optional
from aiokafka import AIOKafkaConsumer, AIOKafkaProducer
from prometheus_client import Counter, Histogram, CONTENT_TYPE_LATEST, generate_latest
from aiohttp import web
from .events import Event, topic_for, kafka_bootstrap
from .kafka import make_consumer, get_producer, next_event, send_event

# Prometheus metrics
DLQ_PROCESSED = Counter('dsrs_dlq_processed_total', 'Total messages processed from DLQ topics', ['topic'])
DLQ_RETRY_SUCCEEDED = Counter('dsrs_dlq_retry_succeeded_total', 'Total DLQ retries that succeeded', ['topic'])
DLQ_RETRY_FAILED = Counter('dsrs_dlq_retry_failed_total', 'Total DLQ retries that failed', ['topic'])
DLQ_RETRY_DURATION = Histogram('dsrs_dlq_retry_seconds', 'Time spent processing a DLQ message')

# Shared handles for readiness checks
_consumer: Optional[AIOKafkaConsumer] = None
_producer: Optional[AIOKafkaProducer] = None

async def _start_health_server(port: int = 8090):
    async def liveness(request):
        return web.json_response({"status": "alive"})

    async def readiness(request):
        # Validate Kafka connectivity via producer metadata
        if _producer is None:
            return web.Response(status=503, text="producer not ready")
        try:
            md = await _producer.client.fetch_all_metadata()
            if not md.brokers:
                return web.Response(status=503, text="no brokers")
        except Exception as e:
            return web.Response(status=503, text=str(e))
        return web.json_response({"status": "ready"})

    async def metrics(request):
        return web.Response(body=generate_latest(), content_type=CONTENT_TYPE_LATEST)

    app = web.Application()
    app.add_routes([
        web.get('/healthz/liveness', liveness),
        web.get('/healthz/readiness', readiness),
        web.get('/metrics', metrics),
    ])
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', port)
    await site.start()

async def dlq_reprocess_loop(group_id: str = "dlq-reprocessor", retry_delay: float = 2.0, max_retries: int = 3):
    global _consumer, _producer
    # Subscribe to all known DLQs
    topics = [
        "registry.household.dlq",
        "eligibility.assessed.dlq",
        "payment.events.dlq",
    ]
    _consumer = await make_consumer(*topics, group_id=group_id)
    _producer = await get_producer()
    try:
        while True:
            msg = await next_event(_consumer)
            topic = msg.topic
            with DLQ_RETRY_DURATION.time():
                evt = Event.from_json(msg.value.decode("utf-8"))
                orig = evt.data.get("original", {})
                original_type = orig.get("type") or evt.type.replace(".dead","")
                original_topic = topic_for(original_type)
                DLQ_PROCESSED.labels(topic=topic).inc()
                ok = False
                for i in range(max_retries):
                    try:
                        await send_event(_producer, original_topic, json.dumps(orig).encode("utf-8"), evt.traceparent)
                        ok = True
                        break
                    except Exception:
                        await asyncio.sleep(retry_delay * (2 ** i))
                if ok:
                    DLQ_RETRY_SUCCEEDED.labels(topic=topic).inc()
                else:
                    DLQ_RETRY_FAILED.labels(topic=topic).inc()
                await _consumer.commit()
    finally:
        if _consumer:
            await _consumer.stop()

async def _main():
    await asyncio.gather(
        _start_health_server(),
        dlq_reprocess_loop(),
    )

if __name__ == "__main__":
    asyncio.run(_main())

