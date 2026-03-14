from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import Resource

from config import settings


def setup_telemetry():
    """
    Initialize OpenTelemetry tracing for the worker service.

    Configures an OTLP exporter that sends trace data to the Jaeger
    collector. The worker is registered as the service 'vortex-worker'
    in the distributed tracing system.

    Returns a tracer instance used throughout the worker runtime.
    """
    resource = Resource(attributes={
        "service.name": "vortex-worker",
    })

    provider = TracerProvider(resource=resource)

    exporter = OTLPSpanExporter(
        endpoint=settings.JAEGER_ENDPOINT
    )

    provider.add_span_processor(
        BatchSpanProcessor(exporter)
    )

    trace.set_tracer_provider(provider)

    return trace.get_tracer(__name__)