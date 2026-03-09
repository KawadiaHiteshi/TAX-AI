from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from pydantic import BaseModel
from models.database import get_db
from models.models import TaxReturn, Document, FilingStatus
from routers.auth import get_current_user
from services.tax_engine import calculate_tax
from services.ai_assistant import chat_with_ai, generate_tax_summary
from datetime import datetime
import json

router = APIRouter()

class TaxCalcRequest(BaseModel):
    tax_year: int = datetime.now().year - 1
    filing_status: str = "single"
    additional_income: float = 0.0
    itemized_deductions: float = 0.0

class ChatRequest(BaseModel):
    message: str
    tax_return_id: int | None = None

@router.post("/calculate")
async def calculate_taxes(
    req: TaxCalcRequest,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    # Pull all processed documents for this year
    result = await db.execute(
        select(Document).where(
            Document.user_id == current_user.id,
            Document.tax_year == req.tax_year,
            Document.status == "done",
        )
    )
    docs = result.scalars().all()

    # Aggregate income and withholding from documents
    total_wages = 0.0
    total_withheld = 0.0
    doc_summary = []

    for doc in docs:
        if doc.extracted_data:
            data = json.loads(doc.extracted_data)
            fields = data.get("tax_fields", {})

            def to_float(val):
                if not val:
                    return 0.0
                cleaned = str(val).replace(",", "").replace("$", "").strip()
                try:
                    return float(cleaned)
                except:
                    return 0.0

            wages = to_float(fields.get("wages")) or to_float(fields.get("nonemployee_compensation"))
            withheld = to_float(fields.get("federal_tax_withheld"))
            total_wages += wages
            total_withheld += withheld
            doc_summary.append({
                "doc_type": doc.doc_type,
                "filename": doc.filename,
                "wages": wages,
                "withheld": withheld,
            })

    total_income = total_wages + req.additional_income
    tax_result = calculate_tax(
        income=total_income,
        filing_status=req.filing_status,
        itemized_deductions=req.itemized_deductions,
        federal_withheld=total_withheld,
    )

    # Upsert TaxReturn record
    existing = await db.execute(
        select(TaxReturn).where(
            TaxReturn.user_id == current_user.id,
            TaxReturn.tax_year == req.tax_year,
        )
    )
    tax_return = existing.scalar_one_or_none()

    ai_summary = generate_tax_summary({**tax_result, "documents": doc_summary})

    if tax_return:
        tax_return.total_income = total_income
        tax_return.total_deductions = tax_result["deduction_amount"]
        tax_return.taxable_income = tax_result["taxable_income"]
        tax_return.tax_owed = tax_result["tax_owed"]
        tax_return.refund_amount = tax_result["refund"]
        tax_return.filing_status = req.filing_status
        tax_return.ai_summary = ai_summary
        tax_return.status = FilingStatus.REVIEW
    else:
        tax_return = TaxReturn(
            user_id=current_user.id,
            tax_year=req.tax_year,
            filing_status=req.filing_status,
            total_income=total_income,
            total_deductions=tax_result["deduction_amount"],
            taxable_income=tax_result["taxable_income"],
            tax_owed=tax_result["tax_owed"],
            refund_amount=tax_result["refund"],
            ai_summary=ai_summary,
            status=FilingStatus.REVIEW,
        )
        db.add(tax_return)

    await db.commit()
    await db.refresh(tax_return)

    return {
        "tax_return_id": tax_return.id,
        "tax_year": req.tax_year,
        "documents_used": doc_summary,
        "calculation": tax_result,
        "ai_summary": ai_summary,
    }

@router.get("/returns")
async def list_returns(
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    result = await db.execute(
        select(TaxReturn).where(TaxReturn.user_id == current_user.id).order_by(TaxReturn.tax_year.desc())
    )
    returns = result.scalars().all()
    return [
        {
            "id": r.id,
            "tax_year": r.tax_year,
            "filing_status": r.filing_status,
            "total_income": r.total_income,
            "tax_owed": r.tax_owed,
            "refund_amount": r.refund_amount,
            "status": r.status,
            "ai_summary": r.ai_summary,
        }
        for r in returns
    ]

@router.post("/approve/{return_id}")
async def approve_return(
    return_id: int,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    result = await db.execute(
        select(TaxReturn).where(TaxReturn.id == return_id, TaxReturn.user_id == current_user.id)
    )
    tax_return = result.scalar_one_or_none()
    if not tax_return:
        raise HTTPException(status_code=404, detail="Tax return not found")
    tax_return.status = FilingStatus.APPROVED
    await db.commit()
    return {"status": "approved", "id": return_id}

@router.post("/chat")
async def tax_chat(
    req: ChatRequest,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    tax_context = None
    if req.tax_return_id:
        result = await db.execute(
            select(TaxReturn).where(
                TaxReturn.id == req.tax_return_id, TaxReturn.user_id == current_user.id
            )
        )
        tax_return = result.scalar_one_or_none()
        if tax_return:
            tax_context = {
                "tax_year": tax_return.tax_year,
                "filing_status": tax_return.filing_status,
                "total_income": tax_return.total_income,
                "total_deductions": tax_return.total_deductions,
                "tax_owed": tax_return.tax_owed,
                "refund_amount": tax_return.refund_amount,
            }

    reply = chat_with_ai(req.message, tax_context)
    return {"reply": reply}
