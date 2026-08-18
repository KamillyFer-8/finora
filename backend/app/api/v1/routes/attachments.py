import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, File, Form, HTTPException, Response, UploadFile, status

from app.api.dependencies import CurrentUser, SessionDep
from app.repositories.attachment import AttachmentRepository
from app.repositories.finance import FinanceRepository
from app.schemas.attachment import AttachmentResponse
from app.services.attachment import AttachmentService
from app.services.storage import LocalStorage, StorageService

router = APIRouter(prefix="/attachments", tags=["attachments"])


def get_storage() -> StorageService:
    return LocalStorage()


StorageDep = Annotated[StorageService, Depends(get_storage)]


@router.post("", response_model=AttachmentResponse, status_code=status.HTTP_201_CREATED)
async def upload_attachment(
    session: SessionDep,
    user: CurrentUser,
    storage: StorageDep,
    file: Annotated[UploadFile, File()],
    transaction_id: Annotated[uuid.UUID | None, Form()] = None,
) -> AttachmentResponse:
    content = await file.read()
    attachment = AttachmentService(
        AttachmentRepository(session), FinanceRepository(session), storage, user.id
    ).create(
        file.filename or "arquivo",
        file.content_type or "application/octet-stream",
        content,
        transaction_id,
    )
    return AttachmentResponse.model_validate(attachment)


@router.get("", response_model=list[AttachmentResponse])
def list_attachments(
    session: SessionDep, user: CurrentUser, transaction_id: uuid.UUID | None = None
) -> list[AttachmentResponse]:
    return [
        AttachmentResponse.model_validate(item)
        for item in AttachmentRepository(session).list(user.id, transaction_id)
    ]


@router.get("/files/{storage_key:path}")
def get_attachment_file(
    storage_key: str, session: SessionDep, user: CurrentUser, storage: StorageDep
) -> Response:
    attachment = AttachmentRepository(session).get_by_storage_key(user.id, storage_key)
    if not attachment:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Anexo não encontrado")
    try:
        content = storage.read(storage_key)
    except FileNotFoundError as error:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Arquivo não encontrado") from error
    return Response(
        content=content,
        media_type=attachment.mime_type,
        headers={"Content-Disposition": f'inline; filename="{attachment.original_name}"'},
    )


@router.delete("/{attachment_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_attachment(
    attachment_id: uuid.UUID, session: SessionDep, user: CurrentUser, storage: StorageDep
) -> Response:
    AttachmentService(
        AttachmentRepository(session), FinanceRepository(session), storage, user.id
    ).delete(attachment_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
