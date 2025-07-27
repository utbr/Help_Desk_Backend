from fastapi import APIRouter
from app.API.auth_routes import router as auth_router
from app.API.user_routes import router as user_router
from app.API.category_routes import router as category_router
from app.API.ticket_routes import router as ticket_router

api_router = APIRouter()

api_router.include_router(auth_router, prefix="/auth", tags=["Auth"])
api_router.include_router(user_router, prefix="/users", tags=["Users"])
api_router.include_router(category_router, prefix="/categories", tags=["Categories"])
api_router.include_router(ticket_router, prefix="/tickets", tags=["Tickets"])
