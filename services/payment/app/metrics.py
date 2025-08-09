from prometheus_client import Counter, Histogram

PAYMENTS_SCHEDULED = Counter('payments_scheduled_total', 'Total payments scheduled')
PAYMENTS_COMPLETED = Counter('payments_completed_total', 'Total payments completed')
PAYMENT_SCHEDULE_TIME = Histogram('payment_schedule_seconds', 'Time to schedule payment')

