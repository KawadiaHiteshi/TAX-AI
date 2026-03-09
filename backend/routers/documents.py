from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from models.database import get_db
from models.models import Document, DocumentType
from routers.auth import get_current_user
from services.document_ai import process_document, extract_tax_fields
import json, os, shutil
from datetime import datetime

router = APIRouter()
UPLOAD_DIR = "./uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

MIME_MAP = {
    "application/pdf": "application/pdf",
    "image/jpeg": "image/jpeg",
    "image/png": "image/png",
    "image/tiff": "image/tiff",
}

async def process_in_background(doc_id: int, file_path: str, mime_type: str, db_url: str):
    """Background task: run Document AI and update the DB record."""
    from models.database import AsyncSessionLocal
    from sqlalchemy import update

    try:
        with open(file_path, "rb") as f:
            file_bytes = f.read()

        extracted = process_document(file_bytes, mime_type)
        tax_fields = extract_tax_fields(extracted)
        merged = {**extracted, "tax_fields": tax_fields}

        async with AsyncSessionLocal() as session:
            await session.execute(
                update(Document)
                .where(Document.id == doc_id)
                .values(
                    status="done",
                    extracted_data=json.dumps(merged),
                    doc_type=extracted.get("doc_type", "other"),
                )
            )
            await session.commit()
    except Exception as e:
        from models.database import AsyncSessionLocal
        from sqlalchemy import update
        async with AsyncSessionLocal() as session:
            await session.execute(
                update(Document).where(Document.id == doc_id).values(status="error")
            )
            await session.commit()

@router.post("/upload")
async def upload_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    tax_year: int = datetime.now().year - 1,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    mime_type = file.content_type
    if mime_type not in MIME_MAP:
        raise HTTPException(status_code=400, detail=f"Unsupported file type: {mime_type}")

    # Save file locally
    save_path = f"{UPLOAD_DIR}/{current_user.id}_{datetime.now().timestamp()}_{file.filename}"
    with open(save_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Create DB record
    doc = Document(
        user_id=current_user.id,
        filename=file.filename,
        file_path=save_path,
        tax_year=tax_year,
        status="processing",
    )
    db.add(doc)
    await db.commit()
    await db.refresh(doc)

    # Process in background
    background_tasks.add_task(
        process_in_background, doc.id, save_path, mime_type, ""
    )

    return {"id": doc.id, "filename": doc.filename, "status": doc.status}

@router.get("/")
async def list_documents(
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    result = await db.execute(
        select(Document).where(Document.user_id == current_user.id).order_by(Document.uploaded_at.desc())
    )
    docs = result.scalars().all()
    return [
        {
            "id": d.id,
            "filename": d.filename,
            "doc_type": d.doc_type,
            "tax_year": d.tax_year,
            "status": d.status,
            "uploaded_at": d.uploaded_at,
            "extracted_data": json.loads(d.extracted_data) if d.extracted_data else None,
        }
        for d in docs
    ]

@router.get("/{doc_id}")
async def get_document(
    doc_id: int,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    result = await db.execute(
        select(Document).where(Document.id == doc_id, Document.user_id == current_user.id)
    )
    doc = result.scalar_one_or_none()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    return {
        "id": doc.id,
        "filename": doc.filename,
        "doc_type": doc.doc_type,
        "tax_year": doc.tax_year,
        "status": doc.status,
        "extracted_data": json.loads(doc.extracted_data) if doc.extracted_data else None,
    }

@router.delete("/{doc_id}")
async def delete_document(
    doc_id: int,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    result = await db.execute(
        select(Document).where(Document.id == doc_id, Document.user_id == current_user.id)
    )
    doc = result.scalar_one_or_none()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    if os.path.exists(doc.file_path):
        os.remove(doc.file_path)
    await db.delete(doc)
    await db.commit()
    return {"deleted": True}
