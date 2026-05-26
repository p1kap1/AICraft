from fastapi import APIRouter
from app.services.model_catalog import get_catalog

router = APIRouter(prefix="/api/models", tags=["models"])

@router.get("/catalog")
def catalog():
    return get_catalog()
