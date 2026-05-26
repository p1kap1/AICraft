from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.payment import Payment
from app.models.billing import UserCredit
import uuid

router = APIRouter(prefix="/api/payment", tags=["payment"])

@router.post("/create")
def create_payment(amount: float = 0, method: str = "alipay", user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    payment = Payment(id=str(uuid.uuid4()), user_id=user.id, amount=amount, method=method)
    db.add(payment); db.commit()
    # Simulate payment success
    payment.status = "completed"
    credit = db.query(UserCredit).filter(UserCredit.user_id == user.id).first()
    if not credit: credit = UserCredit(user_id=user.id, balance=0); db.add(credit)
    credit.balance += amount; db.commit()
    return {"payment_id": payment.id, "status": "completed", "balance": credit.balance}

@router.get("/history")
def payment_history(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return [{"id": p.id, "amount": p.amount, "method": p.method, "status": p.status, "time": p.created_at.isoformat()} for p in db.query(Payment).filter(Payment.user_id == user.id).order_by(Payment.created_at.desc()).limit(20).all()]
