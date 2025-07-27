from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from app.Database.db import get_db
from app.Services.TicketService import TicketService

router = APIRouter()

class TicketCreateRequest(BaseModel):
    title: str
    description: str
    user_id: int
    category_id: int
    priority: Optional[str] = "medium"

class TicketUpdateRequest(BaseModel):
    status: Optional[str] = None
    priority: Optional[str] = None
    assigned_to: Optional[int] = None

class MessageCreateRequest(BaseModel):
    sender_id: int
    message: str

class TicketResponse(BaseModel):
    id: int
    title: str
    description: str
    status: str
    priority: str
    user_id: int
    category_id: int
    assigned_to: Optional[int]
    class Config:
        orm_mode = True


@router.post("/", response_model=TicketResponse, summary="Criar ticket com IA (embeddings)")
def create_ticket(payload: TicketCreateRequest, db: Session = Depends(get_db)):
    ticket = TicketService.create_ticket(
        db,
        title=payload.title,
        description=payload.description,
        user_id=payload.user_id,
        category_id=payload.category_id,
        priority=payload.priority
    )
    return ticket

@router.get("/", response_model=List[TicketResponse], summary="Listar tickets com filtros")
def list_tickets(
    status: Optional[str] = None,
    category_id: Optional[int] = None,
    user_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    return TicketService.list_tickets(db, status, category_id, user_id)

@router.get("/{ticket_id}", response_model=TicketResponse, summary="Obter ticket por ID")
def get_ticket(ticket_id: int, db: Session = Depends(get_db)):
    ticket = TicketService.get_ticket_by_id(db, ticket_id)
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket não encontrado")
    return ticket

@router.put("/{ticket_id}", response_model=TicketResponse, summary="Atualizar ticket")
def update_ticket(ticket_id: int, payload: TicketUpdateRequest, db: Session = Depends(get_db)):
    ticket = TicketService.update_ticket(db, ticket_id, payload.status, payload.priority, payload.assigned_to)
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket não encontrado")
    return ticket

@router.post("/{ticket_id}/messages", summary="Adicionar mensagem ao ticket")
def add_message(ticket_id: int, payload: MessageCreateRequest, db: Session = Depends(get_db)):
    message = TicketService.add_message(db, ticket_id, payload.sender_id, payload.message)
    if not message:
        raise HTTPException(status_code=404, detail="Erro ao adicionar mensagem")
    return {"message": "Mensagem adicionada com sucesso"}
