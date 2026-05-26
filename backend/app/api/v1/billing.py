from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.billing import UserCredit, Order
import uuid

router = APIRouter(prefix="/api/billing", tags=["billing"])

@router.get("/balance")
def get_balance(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    credit = db.query(UserCredit).filter(UserCredit.user_id == user.id).first()
    if not credit:
        credit = UserCredit(user_id=user.id, balance=10.0)
        db.add(credit); db.commit()
    return {"balance": credit.balance, "total_used": credit.total_used}

@router.post("/charge")
def charge(tokens: int = 0, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    cost = tokens * 0.0001  # $0.0001 per token
    credit = db.query(UserCredit).filter(UserCredit.user_id == user.id).first()
    if not credit: credit = UserCredit(user_id=user.id); db.add(credit)
    if credit.balance < cost: raise HTTPException(402, "余额不足")
    credit.balance -= cost
    credit.total_used += cost
    db.commit()
    return {"balance": credit.balance, "cost": cost}

@router.post("/topup")
def topup(amount: float = 10.0, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    credit = db.query(UserCredit).filter(UserCredit.user_id == user.id).first()
    if not credit: credit = UserCredit(user_id=user.id); db.add(credit)
    credit.balance += amount
    order = Order(id=str(uuid.uuid4()), user_id=user.id, amount=amount, credits=amount)
    db.add(order); db.commit()
    return {"balance": credit.balance, "order_id": order.id}

@router.get("/orders")
def list_orders(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return [{"id": o.id, "amount": o.amount, "credits": o.credits, "status": o.status, "created_at": o.created_at.isoformat()} for o in db.query(Order).filter(Order.user_id == user.id).order_by(Order.created_at.desc()).limit(20).all()]
