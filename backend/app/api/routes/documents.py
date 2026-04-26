from pathlib import Path

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import SessionLocal
from app.db.models import Document
from app.schemas.documents import DocumentRead
from app.services.ingestion import IngestionService
from app.services.storage import StorageService
from app.services.vector_store import build_default_vector_store


router = APIRouter(prefix="/documents", tags=["documents"])


def get_db() -> Session:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def build_ingestion_service() -> IngestionService:
    return IngestionService()


def remove_storage_artifacts(storage_path: str) -> None:
    path = Path(storage_path)
    path.unlink(missing_ok=True)
    parent = path.parent
    try:
        if parent.exists() and not any(parent.iterdir()):
            parent.rmdir()
    except OSError:
        return


@router.post("/upload", response_model=DocumentRead, status_code=status.HTTP_201_CREATED)
async def upload_document(file: UploadFile = File(...), db: Session = Depends(get_db)) -> Document:
    filename = file.filename or "document"
    suffix = Path(filename).suffix.lower()
    if suffix not in {".pdf", ".txt"}:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Unsupported file type")

    content = await file.read()
    storage = StorageService(settings.storage_root)
    storage_path = storage.save_upload(filename, content)

    document = Document(
        filename=filename,
        file_type=suffix.lstrip("."),
        storage_path=storage_path,
        status="uploaded",
    )
    try:
        ingestion = build_ingestion_service()
        db.add(document)
        db.flush()
        ingestion.ingest_document(db, document)
        db.commit()
    except Exception as exc:
        db.rollback()
        remove_storage_artifacts(storage_path)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Document ingestion failed") from exc

    db.refresh(document)
    return document


@router.get("", response_model=list[DocumentRead])
def list_documents(db: Session = Depends(get_db)) -> list[Document]:
    return db.query(Document).order_by(Document.upload_time.desc()).all()


@router.get("/{document_id}", response_model=DocumentRead)
def get_document(document_id: int, db: Session = Depends(get_db)) -> Document:
    document = db.get(Document, document_id)
    if document is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")
    return document


@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_document(document_id: int, db: Session = Depends(get_db)) -> None:
    document = db.get(Document, document_id)
    if document is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")

    storage_path = document.storage_path
    build_default_vector_store().delete_document(document.id)
    db.delete(document)
    db.commit()
    remove_storage_artifacts(storage_path)
