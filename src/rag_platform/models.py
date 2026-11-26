import hashlib
from datetime import UTC, datetime
from typing import Any

from pydantic import BaseModel, Field


def utc_now()-> datetime:
    return datetime.now(UTC)

def content_hash(text: str)-> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()

class Transformation(BaseModel):
    type: str
    action: str
    count: int = 0

class Lineage(BaseModel):
    source: str
    source_record_id: str
    source_url: str | None = None
    ingested_at: datetime = Field(default_factory=utc_now)
    run_id: str
    pipeline_version: str = "0.1.0"
    config_hash: str | None = None
    content_hash: str | None = None
    transformation: list[Transformation] = Field(default_factory=list)

class RawDocument(BaseModel):
    source: str
    source_record_id: str
    doc_type: str
    raw_content: str | dict[str, Any]
    metadata: dict[str, Any] = Field(default_factory=dict)

class CleanDocument(BaseModel):
    doc_id: str
    doc_type: str
    text: str = Field(min_length=1)
    metadata: dict[str, Any] = Field(default_factory=dict)
    lineage: Lineage