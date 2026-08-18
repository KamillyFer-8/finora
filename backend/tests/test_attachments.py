import uuid

from test_auth import app, client

from app.api.v1.routes.attachments import get_storage


class FakeStorage:
    deleted: list[str] = []

    def upload(self, user_id: uuid.UUID, filename: str, content: bytes, mime_type: str) -> str:
        return f"users/{user_id}/attachments/{filename}"

    def delete(self, key: str) -> None:
        self.deleted.append(key)

    def get_url(self, key: str) -> str:
        return f"/api/v1/attachments/files/{key}"

    def read(self, key: str) -> bytes:
        return b"conteudo"


def authenticate() -> None:
    email = f"attachments-{uuid.uuid4()}@example.com"
    response = client.post(
        "/api/v1/auth/register",
        json={"name": "Anexos", "email": email, "password": "senha-segura-anexos"},
    )
    assert response.status_code == 201


def test_attachment_upload_list_and_delete() -> None:
    storage = FakeStorage()
    app.dependency_overrides[get_storage] = lambda: storage
    authenticate()

    uploaded = client.post(
        "/api/v1/attachments",
        files={"file": ("recibo.pdf", b"conteudo", "application/pdf")},
    )
    assert uploaded.status_code == 201
    attachment = uploaded.json()
    assert attachment["original_name"] == "recibo.pdf"

    listed = client.get("/api/v1/attachments")
    assert any(item["id"] == attachment["id"] for item in listed.json())
    downloaded = client.get(attachment["url"])
    assert downloaded.status_code == 200
    assert downloaded.content == b"conteudo"
    assert client.delete(f"/api/v1/attachments/{attachment['id']}").status_code == 204
    assert storage.deleted


def test_attachment_rejects_unsupported_content_type() -> None:
    app.dependency_overrides[get_storage] = lambda: FakeStorage()
    authenticate()
    response = client.post(
        "/api/v1/attachments",
        files={"file": ("script.svg", b"<svg/>", "image/svg+xml")},
    )
    assert response.status_code == 415
