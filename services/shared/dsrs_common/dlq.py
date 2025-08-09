from aiokafka import AIOKafkaProducer
from .events import Event, topic_for

async def publish_dlq(producer: AIOKafkaProducer, evt: Event, reason: str):
    dlq_topic = topic_for(evt.type) + ".dlq"
    dead = Event(type=evt.type+".dead", source="dlq", subject=evt.subject, data={"reason": reason, "original": evt.model_dump()})
    await producer.send_and_wait(dlq_topic, dead.to_json().encode("utf-8"))

