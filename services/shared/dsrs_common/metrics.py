from prometheus_client import Counter

EVENTS_CONSUMED = Counter('dsrs_events_consumed_total', 'Total consumed events', ['service','topic'])
EVENTS_PUBLISHED = Counter('dsrs_events_published_total', 'Total published events', ['service','topic'])
EVENTS_FAILED = Counter('dsrs_events_failed_total', 'Total failed events', ['service','topic'])

