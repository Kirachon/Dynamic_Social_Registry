from prometheus_client import Counter, Histogram

ELIGIBILITY_DECISIONS = Counter('eligibility_decisions_total', 'Total eligibility decisions', ['status'])
ELIGIBILITY_PROCESSING_TIME = Histogram('eligibility_processing_seconds', 'Time to process registry event')

