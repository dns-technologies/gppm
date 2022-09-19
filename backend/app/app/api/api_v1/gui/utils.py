from typing import Any
from fastapi import APIRouter, Depends
import app.schemas as schemas
from app.api import deps

router = APIRouter()


@router.get("/public-app-info", response_model=schemas.MsgPublicAppInfo)
def get_public_app_info(
    public_app_info: schemas.MsgPublicAppInfo = Depends(deps.public_app_info),
) -> Any:
    """
    Get public information about this backend instance.
    """

    return public_app_info
