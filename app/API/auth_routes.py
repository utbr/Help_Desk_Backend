from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from app.Database.db import get_db
from app.Services.AuthService import AuthService
from app.Services.UserService import UserService

router = APIRouter()

class RegisterRequest(BaseModel):
    full_name: str
    email: str
    password: str
    role: Optional[str] = "user"

class LoginRequest(BaseModel):
    email: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

class UserResponse(BaseModel):
    id: int
    full_name: str
    email: str
    role: str
    is_active: bool
    class Config:
        orm_mode = True

def get_current_user(token: str = Depends(AuthService.verify_token), db: Session = Depends(get_db)):
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token inválido ou ausente")
    user_id = token.get("sub")
    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Usuário não encontrado")
    user = UserService.get_user_by_id(db, int(user_id))
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuário não existe")
    return user

@router.post("/register", summary="Registrar novo usuário")
def register_user(payload: RegisterRequest, db: Session = Depends(get_db)):
    if UserService.get_user_by_email(db, payload.email):
        raise HTTPException(status_code=400, detail="Email já cadastrado")

    hashed_password = AuthService.hash_password(payload.password)
    user = UserService.create_user(db, payload.full_name, payload.email, hashed_password, payload.role)

    return {"message": "Usuário criado com sucesso", "id": user.id, "email": user.email}


@router.post("/login", response_model=TokenResponse, summary="Fazer login")
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    user = AuthService.authenticate_user(db, payload.email, payload.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Credenciais inválidas")

    token = AuthService.create_access_token({"sub": str(user.id), "email": user.email})
    return {"access_token": token, "token_type": "bearer"}


@router.get("/me", response_model=UserResponse, summary="Obter usuário autenticado")
def get_me(current_user=Depends(get_current_user)):
    return current_user
