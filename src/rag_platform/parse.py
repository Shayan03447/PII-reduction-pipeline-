import re
import unicodedata

from pypdf import PdfReader

from rag_platform.models import CleanDocument, Lineage, RawDocument, content_hash

INVISIBLE_CHARACTERS = "\u200b\ufeff"

SAFE_FIELDS = {
    "ticket": ("ticket_id", "order_id", "status", "created_at"),
    "order": ("order_id", "product", "price", "status", "order_date", "delivery_date"),
    "policy": ("file", "format"),
}

class ParseError(Exception):
    """A record could not be parsed. The message must never contain record content."""

def normalize_text(text: str)-> str:
    text = unicodedata.normalize("NFKC", text)
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = "".join(
        c for c in text
        if c in "\n\t" or (c not in INVISIBLE_CHARACTERS and unicodedata.category(c) != "Cc")
    )
    text = re.sub(r"[ \t]+", " ", text)
    text = "\n".join(line.strip() for line in text.split("\n"))
    return re.sub(r"\n{3,}", "\n\n", text).strip()

def _pdf_text(path: str)-> str:
    try:
        reader = PdfReader(path)
        return "\n\n".join(page.extract_text() or "" for page in reader.pages)
    except Exception as error:
        raise ParseError(f"pdf_error:{type(error).__name__}") from None

def _extract_text(doc: RawDocument)-> str:
    content = doc.raw_content
    if doc.doc_type == "ticket" and isinstance(content, dict):
        body = content.get("body")
        if isinstance(body, str):
            return body
        raise ParseError("missing_body")

    if doc.doc_type == "order" and isinstance(content, dict):
        if not content.get("order_id"):
            raise ParseError("missing_order_id")
        return "\n".join(f"{key}: {value}" for key, value in content.items() if value)

    if doc.doc_type == "policy" and isinstance(content, str):
        return _pdf_text(content) if doc.metadata.get("format") == "pdf" else content
    raise ParseError("unsupported_record")

def parse(doc: RawDocument, run_id: str)-> CleanDocument:
    if "error" in doc.metadata:
        raise ParseError(doc.metadata["error"])
    text = normalize_text(_extract_text(doc))
    if not text:
        raise ParseError("empty_text")
    fields = doc.metadata if doc.doc_type == "policy" else doc.raw_content
    metadata = {key: fields[key] for key in SAFE_FIELDS[doc.doc_type] if key in fields}
    return CleanDocument(
        doc_id =f"{doc.source}: {doc.source_record_id}",
        doc_type = doc.doc_type,
        text=text,
        metadata=metadata,
        lineage=Lineage(
            source=doc.source,
            source_record_id=doc.source_record_id,
            run_id=run_id,
            content_hash=content_hash(text)
        ),
    )


