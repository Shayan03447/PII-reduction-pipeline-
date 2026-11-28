from collections import Counter
from collections.abc import Iterable
from pathlib import Path
from typing import TextIO

from rag_platform.models import CleanDocument


def write_clean(
        docs: Iterable[CleanDocument], clean_dir: str | Path = "data/clean"
) -> dict[str, int]:
    clean_dir = Path(clean_dir)
    clean_dir.mkdir(parents=True, exist_ok=True)
    files: dict[str, TextIO] = {}
    counts : Counter[str] = Counter()
    try:
        for doc in docs:
            source = doc.lineage.source
            if source not in files:
                temp_path = clean_dir / f"{source}.jsonl.tmp"
                files[source] = temp_path.open("w", encoding="utf-8")
            files[source].write(doc.model_dump_json() + "\n")
            counts[source] += 1
    except BaseException:
        for file in files.values():
            file.close()
            Path(file.name).unlink(missing_ok=True)
        raise
    for source, file in files.items():
        file.close()
        Path(file.name).replace(clean_dir / f"{source}.jsonl")
    return dict(counts)