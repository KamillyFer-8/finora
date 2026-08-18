import uuid
from pathlib import Path

import pytest

from app.services.storage import LocalStorage


def test_local_storage_upload_read_url_and_delete(tmp_path: Path) -> None:
    storage = LocalStorage(tmp_path)
    key = storage.upload(uuid.uuid4(), "comprovante.pdf", b"arquivo", "application/pdf")

    assert storage.read(key) == b"arquivo"
    assert storage.get_url(key).startswith("/api/v1/attachments/files/")
    storage.delete(key)
    with pytest.raises(FileNotFoundError):
        storage.read(key)


def test_local_storage_rejects_path_traversal(tmp_path: Path) -> None:
    storage = LocalStorage(tmp_path)
    with pytest.raises(ValueError, match="Chave de armazenamento inválida"):
        storage.read("../fora.txt")
