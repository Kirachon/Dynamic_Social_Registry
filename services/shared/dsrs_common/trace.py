from typing import Optional
from opentelemetry import trace

TRACEPARENT = "traceparent"

def current_traceparent() -> Optional[str]:
    span = trace.get_current_span()
    ctx = span.get_span_context()
    if ctx and ctx.trace_id != 0:
        # W3C traceparent: 00-<trace_id 16 bytes>-<span_id 8 bytes>-01
        trace_id = f"{ctx.trace_id:032x}"
        span_id = f"{ctx.span_id:016x}"
        return f"00-{trace_id}-{span_id}-01"
    return None

