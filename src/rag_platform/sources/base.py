from abc import ABC, abstractmethod
from collections.abc import Iterator

from rag_platform.models import RawDocument

class Source(ABC):
    name: str
    @abstractmethod

    def read(self)-> Iterator[RawDocument]:
        """Yield raw records one at a time (never load everything in memory)."""
