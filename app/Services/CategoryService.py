from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from app.Database.models import TicketCategory, Context
from app.Services.LLMService import LLMService

class CategoryService:

    @staticmethod
    def create_category(db: Session, name: str, context_text: Optional[str] = None):
        """
        Cria uma categoria. Se for passado um texto de contexto, gera embeddings e salva na tabela Context.
        """
        new_category = TicketCategory(name=name)
        db.add(new_category)
        db.commit()
        db.refresh(new_category)

        # Se houver contexto, processar e gerar embeddings
        if context_text:
            CategoryService._generate_context_embeddings(db, new_category.id, context_text)

        return new_category

    @staticmethod
    def list_categories(db: Session) -> List[TicketCategory]:
        return db.query(TicketCategory).all()

    @staticmethod
    def get_category_by_id(db: Session, category_id: int):
        return db.query(TicketCategory).filter(TicketCategory.id == category_id).first()
    
    @staticmethod
    def update_category(db: Session, category_id: int, name: Optional[str] = None, context_text: Optional[str] = None):
        category = db.query(TicketCategory).filter(TicketCategory.id == category_id).first()
        if not category:
            return None

        if name:
            category.name = name
        db.commit()
        db.refresh(category)

        # Se houver novo contexto, gerar embeddings
        if context_text:
            CategoryService._generate_context_embeddings(db, category.id, context_text)

        return category

    @staticmethod
    def delete_category(db: Session, category_id: int):
        category = db.query(TicketCategory).filter(TicketCategory.id == category_id).first()
        if not category:
            return None
        db.delete(category)
        db.commit()
        return True

    @staticmethod
    def add_context_to_category(db: Session, category_id: int, context_text: str):
        """
        Permite adicionar mais contexto a uma categoria existente.
        """
        category = CategoryService.get_category_by_id(db, category_id)
        if not category:
            return None

        CategoryService._generate_context_embeddings(db, category.id, context_text)
        return {"message": "Contexto adicionado com sucesso"}

    @staticmethod
    def _generate_context_embeddings(db: Session, category_id: int, text: str):
        """
        Divide o texto em chunks, gera embeddings e salva na tabela Context.
        """
        chunks = CategoryService._split_text(text)
        for idx, chunk in enumerate(chunks):
            embedding = LLMService.generate_embedding(chunk)
            context = Context(
                category_id=category_id,
                chunk_index=idx,
                chunk_text=chunk,
                embedding=embedding,
                created_at=datetime.utcnow()
            )
            db.add(context)
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
