

from fastapi import APIRouter, Depends
router = APIRouter()

@router.get("/")
async def get_users(services=Depends(get_user_service)):
    return await services.list_users()

    