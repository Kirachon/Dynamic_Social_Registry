from __future__ import annotations
from typing import Optional, List, Tuple
from opentelemetry import trace
from opentelemetry.trace import SpanKind, SpanContext, TraceFlags

TRACEPARENT_HEADER = b"traceparent"

tracer = trace.get_tracer("dsrs.kafka")

def build_headers(traceparent: Optional[str]) -> Optional[List[Tuple[bytes, bytes]]]:
    if not traceparent:
        return None
    return [(TRACEPARENT_HEADER, traceparent.encode("utf-8"))]

def _parse_hex(s: str) -> int:
    try:
        return int(s, 16)
    except Exception:
        return 0

def context_from_traceparent(traceparent: Optional[str]):
    if not traceparent:
        return None
    try:
        parts = traceparent.split("-")
        if len(parts) != 4:
            return None
        version, trace_id_hex, span_id_hex, flags_hex = parts
        sc = SpanContext(
            trace_id=_parse_hex(trace_id_hex),
            span_id=_parse_hex(span_id_hex),
            is_remote=True,
            trace_flags=TraceFlags(_parse_hex(flags_hex)),
            trace_state=None,
        )
        return trace.set_span_in_context(trace.NonRecordingSpan(sc))
    except Exception:
        return None

