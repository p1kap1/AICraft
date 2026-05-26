from fastapi import APIRouter, Depends, HTTPException
import subprocess, uuid
from app.core.security import get_current_user
from app.models.user import User

router = APIRouter(prefix="/api/container", tags=["container"])

@router.post("/run")
def run_container(image: str = "python:3-alpine", code: str = "print('hello')", user: User = Depends(get_current_user)):
    if not user.is_admin: raise HTTPException(403, "admin only")
    cid = f"aicraft-{uuid.uuid4().hex[:8]}"
    try:
        result = subprocess.run(
            ["sudo", "docker", "run", "--rm", "--name", cid, image, "python3", "-c", code],
            capture_output=True, text=True, timeout=30
        )
        return {"container_id": cid, "stdout": result.stdout, "stderr": result.stderr, "exit_code": result.returncode}
    except subprocess.TimeoutExpired:
        return {"error": "timeout"}
    except Exception as e:
        return {"error": str(e)}

@router.get("/status")
def container_status(user: User = Depends(get_current_user)):
    if not user.is_admin: raise HTTPException(403)
    try:
        result = subprocess.run(["sudo", "docker", "ps", "--format", "{{.ID}} {{.Image}} {{.Status}}"], capture_output=True, text=True, timeout=10)
        containers = [{"id": l.split()[0], "image": l.split()[1], "status": " ".join(l.split()[2:])} for l in result.stdout.strip().split("\n") if l]
        return {"containers": containers}
    except Exception as e:
        return {"error": str(e)}
