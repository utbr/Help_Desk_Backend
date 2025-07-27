from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from app.Database.db import get_db
from app.Services.CategoryService import CategoryService

router = APIRouter()
class CategoryCreateRequest(BaseModel):
    name: str
    context_text: Optional[str] = None

class CategoryUpdateRequest(BaseModel):
    name: Optional[str] = None
    context_text: Optional[str] = None

class ContextAddRequest(BaseModel):
    context_text: str

class CategoryResponse(BaseModel):
    id: int
    name: str
    class Config:
        orm_mode = True


@router.post("/", response_model=CategoryResponse, summary="Criar categoria com contexto opcional")
def create_category(payload: CategoryCreateRequest, db: Session = Depends(get_db)):
    category = CategoryService.create_category(db, payload.name, payload.context_text)
    return category

@router.get("/", response_model=List[CategoryResponse], summary="Listar categorias")
def list_categories(db: Session = Depends(get_db)):
    return CategoryService.list_categories(db)

@router.put("/{category_id}", response_model=CategoryResponse, summary="Atualizar nome e/ou adicionar contexto")
def update_category(category_id: int, payload: CategoryUpdateRequest, db: Session = Depends(get_db)):
    category = CategoryService.update_category(db, category_id, payload.name, payload.context_text)
    if not category:
        raise HTTPException(status_code=404, detail="Categoria não encontrada")
    return category

@router.post("/{category_id}/context", summary="Adicionar contexto extra à categoria")
def add_context(category_id: int, payload: ContextAddRequest, db: Session = Depends(get_db)):
    result = CategoryService.add_context_to_category(db, category_id, payload.context_text)
    if not result:
        raise HTTPException(status_code=404, detail="Categoria não encontrada")
    return {"message": "Contexto adicionado com sucesso"}

@router.delete("/{category_id}", summary="Excluir categoria")
def delete_category(category_id: int, db: Session = Depends(get_db)):
    deleted = CategoryService.delete_category(db, category_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Categoria não encontrada")
    return {"message": "Categoria removida com sucesso"}
