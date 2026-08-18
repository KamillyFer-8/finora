import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.attachment import Attachment


class AttachmentRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def create(self, attachment: Attachment) -> Attachment:
        self.session.add(attachment)
        self.session.commit()
        return attachment

    def list(self, user_id: uuid.UUID, transaction_id: uuid.UUID | None = None) -> list[Attachment]:
        query = select(Attachment).where(Attachment.user_id == user_id)
        if transaction_id:
            query = query.where(Attachment.transaction_id == transaction_id)
        return list(self.session.scalars(query.order_by(Attachment.created_at.desc())))

    def get(self, user_id: uuid.UUID, attachment_id: uuid.UUID) -> Attachment | None:
        return self.session.scalar(
            select(Attachment).where(Attachment.id == attachment_id, Attachment.user_id == user_id)
        )

    def get_by_storage_key(self, user_id: uuid.UUID, storage_key: str) -> Attachment | None:
        return self.session.scalar(
            select(Attachment).where(
                Attachment.user_id == user_id, Attachment.storage_key == storage_key
            )
        )

    def delete(self, attachment: Attachment) -> None:
        self.session.delete(attachment)
        self.session.commit()
