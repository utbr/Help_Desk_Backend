from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from app.Database.db import get_db
from app.Services.UserService import UserService

router = APIRouter()

class UserCreateRequest(BaseModel):
    full_name: str
    email: str
    password: str
    role: Optional[str] = "user"

class UserUpdateRequest(BaseModel):
    full_name: Optional[str] = None
    role: Optional[str] = None
    is_active: Optional[bool] = None

class UserResponse(BaseModel):
    id: int
    full_name: str
    email: str
    role: str
    is_active: bool
    class Config:
        orm_mode = True


@router.get("/", response_model=List[UserResponse], summary="Listar todos os usuários")
def list_users(db: Session = Depends(get_db)):
    return UserService.list_users(db)

@router.get("/{user_id}", response_model=UserResponse, summary="Obter usuário por ID")
def get_user(user_id: int, db: Session = Depends(get_db)):
    user = UserService.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    return user

@router.post("/", response_model=UserResponse, summary="Criar usuário")
def create_user(payload: UserCreateRequest, db: Session = Depends(get_db)):
    if UserService.get_user_by_email(db, payload.email):
        raise HTTPException(status_code=400, detail="Email já cadastrado")

    from app.Services.AuthService import AuthService
    hashed_password = AuthService.hash_password(payload.password)

    user = UserService.create_user(db, payload.full_name, payload.email, hashed_password, payload.role)
    return user

@router.put("/{user_id}", response_model=UserResponse, summary="Atualizar usuário")
def update_user(user_id: int, payload: UserUpdateRequest, db: Session = Depends(get_db)):
    user = UserService.update_user(db, user_id, payload.full_name, payload.role, payload.is_active)
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    return user

@router.delete("/{user_id}", summary="Excluir usuário")
def delete_user(user_id: int, db: Session = Depends(get_db)):
    deleted = UserService.delete_user(db, user_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    return {"message": "Usuário removido com sucesso"}
