import re
import uuid
from pathlib import Path
from typing import Protocol

from app.core.config import settings


class StorageService(Protocol):
    def upload(self, user_id: uuid.UUID, filename: str, content: bytes, mime_type: str) -> str: ...

    def delete(self, key: str) -> None: ...

    def get_url(self, key: str) -> str: ...

    def read(self, key: str) -> bytes: ...


class LocalStorage:
    def __init__(self, root: Path | None = None) -> None:
        self.root = (root or settings.upload_dir).resolve()
        self.root.mkdir(parents=True, exist_ok=True)

    def upload(self, user_id: uuid.UUID, filename: str, content: bytes, mime_type: str) -> str:
        del mime_type
        safe_name = re.sub(r"[^a-zA-Z0-9._-]", "-", filename)[:120]
        key = f"users/{user_id}/attachments/{uuid.uuid4()}-{safe_name}"
        target = self._path(key)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(content)
        return key

    def delete(self, key: str) -> None:
        target = self._path(key)
        if target.exists():
            target.unlink()

    def get_url(self, key: str) -> str:
        return f"{settings.api_v1_prefix}/attachments/files/{key}"

    def read(self, key: str) -> bytes:
        return self._path(key).read_bytes()

    def _path(self, key: str) -> Path:
        target = (self.root / key).resolve()
        if self.root not in target.parents:
            raise ValueError("Chave de armazenamento inválida")
        return target
