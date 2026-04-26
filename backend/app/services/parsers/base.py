from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path

from app.domain.documents import StructuredDocument


class BaseParser(ABC):
    @abstractmethod
    def parse(self, path: Path) -> StructuredDocument:
        """Parse the file at ``path`` into a structured document."""

