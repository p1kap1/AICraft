from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.sso import SsoProvider, SsoSession
from app.core.security import create_token
import uuid, secrets, datetime as dt

router = APIRouter(prefix="/api/sso", tags=["sso"])

@router.get("/providers")
def list_providers(db: Session = Depends(get_db)):
    providers = db.query(SsoProvider).filter(SsoProvider.enabled == True).all()
    if not providers:
        # Seed defaults
        for name, ptype in [("GitHub","github"),("Google","google"),("WeChat","wechat")]:
            p = SsoProvider(id=str(uuid.uuid4()), name=name, provider_type=ptype,
                client_id=f"{ptype}-client-id", client_secret=f"{ptype}-secret")
            db.add(p)
        db.commit()
        providers = db.query(SsoProvider).filter(SsoProvider.enabled == True).all()
    return [{"id": p.id, "name": p.name, "type": p.provider_type, "enabled": p.enabled} for p in providers]

@router.get("/login/{provider_id}")
def sso_login(provider_id: str, db: Session = Depends(get_db)):
    provider = db.query(SsoProvider).filter(SsoProvider.id == provider_id).first()
    if not provider: raise HTTPException(404, "Provider not found")
    state = secrets.token_urlsafe(32)
    session = SsoSession(id=str(uuid.uuid4()), state=state, expires_at=dt.datetime.utcnow() + dt.timedelta(minutes=10))
    db.add(session); db.commit()
    auth_url = f"https://{provider.provider_type}.com/login/oauth/authorize?client_id={provider.client_id}&state={state}&redirect_uri=/api/sso/callback/{provider_id}"
    return RedirectResponse(auth_url)

@router.get("/callback/{provider_id}")
def sso_callback(provider_id: str, state: str = "", code: str = "", db: Session = Depends(get_db)):
    session = db.query(SsoSession).filter(SsoSession.state == state).first()
    if not session or session.expires_at < dt.datetime.utcnow():
        raise HTTPException(400, "Invalid or expired state")
    # Simulated: create/return token (in prod, would verify with provider)
    token = create_token("sso-user-" + str(uuid.uuid4())[:8])
    return {"token": token, "message": "SSO login successful"}
