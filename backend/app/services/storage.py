from pathlib import Path
from uuid import uuid4


class StorageService:
    def __init__(self, root: str) -> None:
        self.root = Path(root)

    def save_upload(self, filename: str, content: bytes) -> str:
        safe_name = Path(filename).name or "document"
        document_dir = self.root / "raw" / str(uuid4())
        document_dir.mkdir(parents=True, exist_ok=True)

        destination = document_dir / safe_name
        destination.write_bytes(content)
        return str(destination)

