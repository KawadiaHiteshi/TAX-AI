from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from pydantic import BaseModel
import stripe, os
from models.database import get_db
from models.models import TaxReturn, Payment, FilingStatus
from routers.auth import get_current_user

router = APIRouter()
stripe.api_key = os.getenv("STRIPE_SECRET_KEY", "")

class PaymentRequest(BaseModel):
    tax_return_id: int
    payment_method_id: str   # from Stripe.js on the frontend

@router.post("/create-intent")
async def create_payment_intent(
    tax_return_id: int,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    result = await db.execute(
        select(TaxReturn).where(
            TaxReturn.id == tax_return_id,
            TaxReturn.user_id == current_user.id,
            TaxReturn.status == FilingStatus.APPROVED,
        )
    )
    tax_return = result.scalar_one_or_none()
    if not tax_return:
        raise HTTPException(status_code=404, detail="Approved tax return not found")

    if tax_return.tax_owed <= 0:
        raise HTTPException(status_code=400, detail="No payment due — you have a refund!")

    amount_cents = int(tax_return.tax_owed * 100)
    intent = stripe.PaymentIntent.create(
        amount=amount_cents,
        currency="usd",
        metadata={
            "user_id": current_user.id,
            "tax_return_id": tax_return.id,
            "tax_year": tax_return.tax_year,
        },
    )

    payment = Payment(
        user_id=current_user.id,
        tax_return_id=tax_return.id,
        amount=tax_return.tax_owed,
        stripe_payment_intent=intent.id,
        status="pending",
    )
    db.add(payment)
    await db.commit()

    return {
        "client_secret": intent.client_secret,
        "amount": tax_return.tax_owed,
        "payment_id": payment.id,
    }

@router.post("/confirm")
async def confirm_payment(
    req: PaymentRequest,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    result = await db.execute(
        select(TaxReturn).where(
            TaxReturn.id == req.tax_return_id,
            TaxReturn.user_id == current_user.id,
        )
    )
    tax_return = result.scalar_one_or_none()
    if not tax_return:
        raise HTTPException(status_code=404, detail="Tax return not found")

    # In a real app, you'd verify the Stripe webhook instead
    tax_return.status = FilingStatus.PAID
    await db.commit()

    return {"status": "paid", "message": "Payment confirmed. Your taxes have been filed!"}

@router.get("/history")
async def payment_history(
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    result = await db.execute(
        select(Payment).where(Payment.user_id == current_user.id).order_by(Payment.created_at.desc())
    )
    payments = result.scalars().all()
    return [
        {
            "id": p.id,
            "amount": p.amount,
            "status": p.status,
            "created_at": p.created_at,
            "tax_return_id": p.tax_return_id,
        }
        for p in payments
    ]
