from types import SimpleNamespace

from fastapi import FastAPI
from opentelemetry import trace
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.httpx import HTTPXClientInstrumentor
from opentelemetry.instrumentation.redis import RedisInstrumentor
from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor
from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter
from opentelemetry.trace import SpanKind
from pytest import MonkeyPatch
from sqlalchemy import create_engine, text

from app.config.settings import Settings
from app.shared import telemetry


def test_existing_database_engine_exports_query_spans(monkeypatch: MonkeyPatch) -> None:
    # Match application startup: create the engine before configuring telemetry.
    database_engine = create_engine("sqlite:///:memory:")
    exporter = InMemorySpanExporter()
    provider = TracerProvider()
    app = FastAPI()

    def memory_exporter(*, endpoint: str) -> InMemorySpanExporter:
        return exporter

    def set_provider(_provider: TracerProvider) -> None:
        # Keep the process-wide provider untouched for the rest of the suite.
        pass

    monkeypatch.setattr(telemetry, "engine", SimpleNamespace(sync_engine=database_engine))
    monkeypatch.setattr(telemetry, "TracerProvider", lambda **kwargs: provider)
    monkeypatch.setattr(telemetry, "BatchSpanProcessor", SimpleSpanProcessor)
    monkeypatch.setattr(telemetry, "OTLPSpanExporter", memory_exporter)
    monkeypatch.setattr(trace, "set_tracer_provider", set_provider)
    monkeypatch.setattr(trace, "get_tracer_provider", lambda: provider)

    try:
        telemetry.configure_telemetry(Settings(otel_enabled=True), app)
        with database_engine.connect() as connection:
            assert connection.execute(text("SELECT 1")).scalar_one() == 1

        query_spans = [
            span
            for span in exporter.get_finished_spans()
            if span.attributes and span.attributes.get("db.statement") == "SELECT 1"
        ]
        assert len(query_spans) == 1
        assert query_spans[0].kind is SpanKind.CLIENT
    finally:
        FastAPIInstrumentor.uninstrument_app(app)
        HTTPXClientInstrumentor().uninstrument()
        RedisInstrumentor().uninstrument()
        SQLAlchemyInstrumentor().uninstrument()
        provider.shutdown()
        database_engine.dispose()
