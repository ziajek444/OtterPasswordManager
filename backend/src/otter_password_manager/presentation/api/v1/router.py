from fastapi import APIRouter

from otter_password_manager.presentation.api.v1.users import router as users_router

router = APIRouter()
router.include_router(users_router)

