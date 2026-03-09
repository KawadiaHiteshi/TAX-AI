from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from pydantic import BaseModel
from models.database import get_db
from models.models import TaxReturn
from routers.auth import get_current_user
from services.state_tax_engine import (
    calculate_state_tax,
    calculate_combined_tax,
    list_states,
)
from services.tax_engine import calculate_tax
from datetime import datetime

router = APIRouter()


class StateTaxRequest(BaseModel):
    state_code: str
    income: float
    filing_status: str = "single"
    itemized_deductions: float = 0.0


class CombinedTaxRequest(BaseModel):
    state_code: str
    tax_year: int = datetime.now().year - 1
    filing_status: str = "single"
    additional_income: float = 0.0
    itemized_deductions: float = 0.0


@router.get("/states")
def get_all_states():
    """List all 50 states + DC with top rate info."""
    return list_states()


@router.post("/calculate")
def calculate_single_state(req: StateTaxRequest):
    """Calculate state-only tax for a given state and income."""
    result = calculate_state_tax(
        state_code=req.state_code,
        income=req.income,
        filing_status=req.filing_status,
        itemized_deductions=req.itemized_deductions,
    )
    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])
    return result


@router.post("/combined")
async def calculate_combined(
    req: CombinedTaxRequest,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """
    Calculate federal + state tax together.
    Optionally pulls income from the user's processed documents.
    """
    from models.models import Document
    import json

    # Pull documents for this tax year
    result = await db.execute(
        select(Document).where(
            Document.user_id == current_user.id,
            Document.tax_year == req.tax_year,
            Document.status == "done",
        )
    )
    docs = result.scalars().all()

    total_wages = 0.0
    total_withheld = 0.0
    for doc in docs:
        if doc.extracted_data:
            data = json.loads(doc.extracted_data)
            fields = data.get("tax_fields", {})

            def to_float(val):
                if not val:
                    return 0.0
                try:
                    return float(str(val).replace(",", "").replace("$", "").strip())
                except:
                    return 0.0

            wages = to_float(fields.get("wages")) or to_float(fields.get("nonemployee_compensation"))
            withheld = to_float(fields.get("federal_tax_withheld"))
            total_wages += wages
            total_withheld += withheld

    total_income = total_wages + req.additional_income

    # Federal calculation
    federal_result = calculate_tax(
        income=total_income,
        filing_status=req.filing_status,
        itemized_deductions=req.itemized_deductions,
        federal_withheld=total_withheld,
    )

    # Combined federal + state
    combined = calculate_combined_tax(
        state_code=req.state_code,
        federal_result=federal_result,
        filing_status=req.filing_status,
        itemized_deductions=req.itemized_deductions,
    )

    return combined


@router.get("/compare")
def compare_states(
    income: float = 100000,
    filing_status: str = "single",
):
    """
    Compare tax burden across all states for a given income.
    Returns sorted list from lowest to highest state tax.
    """
    from services.state_tax_engine import STATE_TAX_DATA

    results = []
    for code in STATE_TAX_DATA:
        r = calculate_state_tax(
            state_code=code,
            income=income,
            filing_status=filing_status,
        )
        results.append({
            "state": r["state"],
            "state_code": r["state_code"],
            "tax_owed": r["tax_owed"],
            "effective_rate": r["effective_rate"],
            "has_income_tax": r["has_income_tax"],
        })

    return sorted(results, key=lambda x: x["tax_owed"])
