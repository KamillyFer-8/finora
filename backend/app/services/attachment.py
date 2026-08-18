import uuid

from fastapi import HTTPException, status

from app.core.config import settings
from app.models.attachment import Attachment
from app.repositories.attachment import AttachmentRepository
from app.repositories.finance import FinanceRepository
from app.services.storage import StorageService

ALLOWED_MIME_TYPES = {"application/pdf", "image/jpeg", "image/png"}


class AttachmentService:
    def __init__(
        self,
        repository: AttachmentRepository,
        finance: FinanceRepository,
        storage: StorageService,
        user_id: uuid.UUID,
    ) -> None:
        self.repository = repository
        self.finance = finance
        self.storage = storage
        self.user_id = user_id

    def create(
        self, filename: str, mime_type: str, content: bytes, transaction_id: uuid.UUID | None
    ) -> Attachment:
        if mime_type not in ALLOWED_MIME_TYPES:
            raise HTTPException(status.HTTP_415_UNSUPPORTED_MEDIA_TYPE, "Formato não permitido")
        if not content or len(content) > settings.max_attachment_bytes:
            raise HTTPException(
                status.HTTP_413_CONTENT_TOO_LARGE, "Arquivo vazio ou maior que 10 MB"
            )
        if transaction_id and not self.finance.get_transaction(self.user_id, transaction_id):
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Transação não encontrada")
        key = self.storage.upload(self.user_id, filename, content, mime_type)
        url = self.storage.get_url(key)
        return self.repository.create(
            Attachment(
                user_id=self.user_id,
                transaction_id=transaction_id,
                original_name=filename[:255],
                storage_key=key,
                url=url,
                mime_type=mime_type,
                size=len(content),
            )
        )

    def delete(self, attachment_id: uuid.UUID) -> None:
        attachment = self.repository.get(self.user_id, attachment_id)
        if not attachment:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Anexo não encontrado")
        self.storage.delete(attachment.storage_key)
        self.repository.delete(attachment)
