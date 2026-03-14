"""
The Panopticon: All OpenTelemetry setup lives here.
"""

from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.sdk.resources import Resource
from opentelemetry.instrumentation.requests import RequestsInstrumentor
from opentelemetry.instrumentation.httpx import HTTPXClientInstrumentor

from config import settings


def setup_telemetry(app):
    resource = Resource(attributes={"service.name": "vortex-api"})
    provider = TracerProvider(resource=resource)

    exporter = OTLPSpanExporter(endpoint=settings.JAEGER_ENDPOINT)

    processor = BatchSpanProcessor(exporter)
    provider.add_span_processor(processor)

    trace.set_tracer_provider(provider)

    RequestsInstrumentor().instrument()
    HTTPXClientInstrumentor().instrument()

    FastAPIInstrumentor.instrument_app(app)

    return trace.get_tracer(__name__)