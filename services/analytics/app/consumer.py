from pymongo import MongoClient
from dsrs_common.kafka import make_consumer, next_event
from dsrs_common.events import Event

class AnalyticsStore:
    def __init__(self, mongo_url: str):
        self.client = MongoClient(mongo_url)
        self.db = self.client.get_database()
        self.col = self.db.get_collection("metrics")
        self.col.create_index("_id", unique=True)
        self.col.update_one({"_id":"summary"}, {"$setOnInsert": {"assessed":0, "approved":0, "payments_scheduled":0, "payments_completed":0}}, upsert=True)

    def inc(self, field: str, amount: int = 1):
        self.col.update_one({"_id":"summary"}, {"$inc": {field: amount}})

async def consume_analytics(mongo_url: str):
    store = AnalyticsStore(mongo_url)
    consumer = await make_consumer("eligibility.assessed", "payment.events", group_id="analytics")
    try:
        while True:
            msg = await next_event(consumer)
            evt = Event.from_json(msg.value.decode("utf-8"))
            if evt.type.startswith("eligibility.assessed"):
                store.inc("assessed", 1)
                if evt.type.endswith("approved"):
                    store.inc("approved", 1)
            elif evt.type == "payment.scheduled":
                store.inc("payments_scheduled", 1)
            elif evt.type == "payment.completed":
                store.inc("payments_completed", 1)
            await consumer.commit()
    finally:
        await consumer.stop()

