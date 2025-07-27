from sqlalchemy.orm import Session
from typing import List, Optional
from app.Database.models import Ticket, TicketMessage, TicketHistory, Context
from app.Services.LLMService import LLMService
from datetime import datetime

class TicketService:

    @staticmethod
    def create_ticket(db: Session, title: str, description: str, user_id: int, category_id: int, priority: str = "medium"):
        new_ticket = Ticket(
            title=title,
            description=description,
            status="open",
            priority=priority,
            user_id=user_id,
            category_id=category_id
        )
        db.add(new_ticket)
        db.commit()
        db.refresh(new_ticket)

        # Registrar histórico
        TicketService._log_history(db, new_ticket.id, f"Ticket criado por usuário {user_id}", user_id) # Pensar melhor nisso

        # Gerar embeddings (IA) com base no título + descrição
        chunks = TicketService._split_text(f"{title}\n\n{description}")
        LLMService.store_embedding(db, new_ticket.id, chunks) # Colocar um interpretador de imagem?

        return new_ticket

    @staticmethod
    def list_tickets(db: Session, status: Optional[str] = None, category_id: Optional[int] = None, user_id: Optional[int] = None) -> List[Ticket]:
        query = db.query(Ticket)
        if status:
            query = query.filter(Ticket.status == status)
        if category_id:
            query = query.filter(Ticket.category_id == category_id)
        if user_id:
            query = query.filter(Ticket.user_id == user_id)
        return query.all()


    @staticmethod
    def get_ticket_by_id(db: Session, ticket_id: int):
        return db.query(Ticket).filter(Ticket.id == ticket_id).first()

    @staticmethod
    def update_ticket(db: Session, ticket_id: int, status: Optional[str] = None, priority: Optional[str] = None, assigned_to: Optional[int] = None):
        ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
        if not ticket:
            return None

        changes = []
        if status and ticket.status != status:
            ticket.status = status
            changes.append(f"Status alterado para {status}")
        if priority and ticket.priority != priority:
            ticket.priority = priority
            changes.append(f"Prioridade alterada para {priority}")
        if assigned_to and ticket.assigned_to != assigned_to:
            ticket.assigned_to = assigned_to
            changes.append(f"Atribuído ao usuário {assigned_to}")

        ticket.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(ticket)

        # Registrar histórico
        for change in changes:
            TicketService._log_history(db, ticket.id, change, assigned_to or ticket.user_id)

        return ticket

    @staticmethod
    def add_message(db: Session, ticket_id: int, sender_id: int, message: str):
        new_message = TicketMessage(ticket_id=ticket_id, sender_id=sender_id, message=message)
        db.add(new_message)
        db.commit()
        db.refresh(new_message)

        # Registrar histórico
        TicketService._log_history(db, ticket_id, f"Mensagem adicionada pelo usuário {sender_id}", sender_id)

        return new_message

    @staticmethod
    def _log_history(db: Session, ticket_id: int, action: str, performed_by: int):
        log = TicketHistory(ticket_id=ticket_id, action=action, performed_by=performed_by)
        db.add(log)
        db.commit()

    @staticmethod
    def _split_text(text: str, chunk_size: int = 400) -> List[str]:
        words = text.split()
        chunks = []
        current_chunk = []
        current_length = 0

        for word in words:
            if current_length + len(word) + 1 > chunk_size:
                chunks.append(" ".join(current_chunk))
                current_chunk = []
                current_length = 0
            current_chunk.append(word)
            current_length += len(word) + 1

        if current_chunk:
            chunks.append(" ".join(current_chunk))

        return chunks
