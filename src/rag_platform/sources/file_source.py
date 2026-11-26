import csv
import json
from collections.abc import Iterator
from pathlib import Path

from rag_platform.models import RawDocument
from rag_platform.sources.base import Source


class FileSource(Source):
    """Read raw record from local files."""
    name = "files"

    def __init__(self, raw_dir: str | Path = "data/raw")-> None:
        self.raw_dir = Path(raw_dir)

    def read(self)-> Iterator[RawDocument]:
        """Yeild all tickets, ten orders and then docs"""
        yield from self._read_tickets()
        yield from self._read_orders()
        yield from self._read_docs()

    def _read_tickets(self)-> Iterator[RawDocument]:
        path = self.raw_dir / "tickets.jsonl"
        with path.open(encoding="utf-8-sig", errors="replace") as f:
            for line_no, line in enumerate(f, start=1):
                if not line.strip():
                    continue
                metadata = {"file": path.name, "line": line_no}
                try:
                    record = json.loads(line)
                except json.JSONDecodeError:
                    record = None
                if isinstance(record, dict):
                    record_id = str(record.get("ticket_id") or f"line-{line_no}")
                    content = record
                else:
                    metadata["error"] = "invalid json"
                    record_id = f"line-{line_no}"
                    content = line
                yield RawDocument(
                    source="tickets", source_record_id=record_id,
                    doc_type="ticket", raw_content=content, metadata=metadata,
                )

    def _read_orders(self)->Iterator[RawDocument]:
        path = self.raw_dir / "orders.csv"
        with path.open(encoding="utf-8-sig", errors="replace", newline="") as f:
            reader = csv.DictReader(f)
            for row in reader:
                metadata = {"file": path.name, "line": reader.line_num}
                if None in row:
                    row["_extra"] = row.pop(None)
                    metadata["error"] = "extra_columns"
                yield RawDocument(
                    source = "orders",
                    source_record_id = row.get("order_id") or f"line-{reader.line_num}", 
                    doc_type = "order", raw_content=row, metadata=metadata,
                )

    def _read_docs(self)-> Iterator[RawDocument]:
        for path in sorted((self.raw_dir / "docs").glob("*")):
            suffix = path.suffix.lower()
            if suffix == ".md":
                content = path.read_text(encoding= "utf-8-sig", errors="replace")
            elif suffix == ".pdf":
                content = str(path)
            else:
                continue
            yield RawDocument(
                source = "docs", source_record_id = path.name, doc_type = "policy",
                raw_content = content,
                metadata = {"file": path.name, "format": suffix[1:]},
            )


