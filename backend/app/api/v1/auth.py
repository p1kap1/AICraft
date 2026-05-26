"""认证 API - 注册 / 登录"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import hash_password, verify_password, create_token, get_current_user
from app.models.user import User
from app.schemas.common import RegisterRequest, LoginRequest, TokenResponse, ApiResponse

router = APIRouter(prefix="/api", tags=["auth"])


@router.post("/register", response_model=ApiResponse)
def register(req: RegisterRequest, db: Session = Depends(get_db)):
    # 检查已存在
    if req.email:
        exists = db.query(User).filter(User.email == req.email).first()
        if exists:
            raise HTTPException(400, "邮箱已注册")
    if req.phone:
        exists = db.query(User).filter(User.phone == req.phone).first()
        if exists:
            raise HTTPException(400, "手机号已注册")

    user = User(
        email=req.email,
        phone=req.phone,
        nickname=req.nickname,
        hashed_password=hash_password(req.password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return ApiResponse(message="注册成功")


@router.post("/login", response_model=TokenResponse)
def login(req: LoginRequest, db: Session = Depends(get_db)):
    user = (
        db.query(User)
        .filter((User.email == req.account) | (User.phone == req.account))
        .first()
    )
    if not user or not verify_password(req.password, user.hashed_password):
        raise HTTPException(400, "账号或密码错误")

    token = create_token(user.id)
    return TokenResponse(token=token, user_id=user.id, nickname=user.nickname)


@router.get("/me")
def me(user: User = Depends(get_current_user)):
    return {
        "id": user.id,
        "email": user.email,
        "phone": user.phone,
        "nickname": user.nickname,
    }
