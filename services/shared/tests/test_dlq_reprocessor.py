import os
import pytest
import asyncio
from testcontainers.kafka import KafkaContainer
from dsrs_common.events import Event
from dsrs_common.kafka import get_producer, make_consumer, next_event
from dsrs_common.dlq import publish_dlq
from dsrs_common.dlq_reprocessor import dlq_reprocess_loop

@pytest.mark.asyncio
async def test_dlq_reprocessor_recovers_message():
    with KafkaContainer() as kafka:
        os.environ['KAFKA_BROKERS'] = kafka.get_bootstrap_server()
        prod = await get_producer()
        # Publish a dead-letter event for eligibility.assessed.approved
        original = Event(type="eligibility.assessed.approved", source="eligibility", subject="H1", data={"id":"H1","status":"approved"})
        dead = Event(type="eligibility.assessed.approved.dead", source="dlq", subject="H1", data={"original": original.model_dump()})
        await prod.send_and_wait("eligibility.assessed.dlq", dead.to_json().encode("utf-8"))
        # Start reprocessor
        task = asyncio.create_task(dlq_reprocess_loop(max_retries=2, retry_delay=0.2))
        # Consume from original topic to confirm retry produced it
        consumer = await make_consumer("eligibility.assessed", group_id="test-confirm")
        try:
            msg = await asyncio.wait_for(next_event(consumer), timeout=10)
            assert msg.topic == "eligibility.assessed"
        finally:
            task.cancel()
            await consumer.stop()

