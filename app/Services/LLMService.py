import os
from typing import List, Dict, Any
from sqlalchemy.orm import Session
from openai import OpenAI
from app.Database.db import get_db
from app.Database.models import Context
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
EMBEDDING_MODEL = os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small")
CHAT_MODEL = os.getenv("OPENAI_CHAT_MODEL", "gpt-4o-mini")

client = OpenAI(api_key=OPENAI_API_KEY)

class LLMService:

    @staticmethod
    def generate_embedding(text: str) -> List[float]:
        """
        Gera embedding usando OpenAI e retorna vetor.
        """
        response = client.embeddings.create(
            input=text,
            model=EMBEDDING_MODEL
        )
        return response.data[0].embedding

    @staticmethod
    def store_embedding(db: Session, ticket_id: int, chunks: List[str]):
        """
        Divide texto em chunks, gera embeddings e armazena no banco.
        """
        for idx, chunk in enumerate(chunks):
            embedding = LLMService.generate_embedding(chunk)
            context_entry = Context(
                ticket_id=ticket_id,
                chunk_index=idx,
                chunk_text=chunk,
                embedding=embedding
            )
            db.add(context_entry)
        db.commit()

    @staticmethod
    def search_similar(db: Session, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Busca contexto semântico no banco usando pgvector.
        """
        query_embedding = LLMService.generate_embedding(query)

        sql = """
        SELECT ticket_id, chunk_text, 1 - (embedding <=> %s) AS similarity
        FROM context
        ORDER BY embedding <=> %s
        LIMIT %s
        """
        result = db.execute(sql, (query_embedding, query_embedding, top_k)).fetchall()

        return [{"ticket_id": row[0], "text": row[1], "score": float(row[2])} for row in result]

    @staticmethod
    def generate_response(db: Session, user_message: str, top_k: int = 5) -> str:
        """
        Gera resposta utilizando contexto do banco (RAG).
        Passos:
        1. Busca os chunks mais relevantes
        2. Monta um prompt com esses chunks
        3. Envia para o modelo de chat da OpenAI
        """

        # 1. Buscar os chunks mais relevantes
        relevant_chunks = LLMService.search_similar(db, user_message, top_k=top_k)

        # 2. Criar um contexto com os chunks
        context_text = "\n\n".join([f"- {chunk['text']}" for chunk in relevant_chunks])
        system_prompt = (
            "Você é um assistente de suporte técnico.\n"
            "Use as informações abaixo como contexto para responder:\n"
            f"{context_text}\n\n"
            "Se a informação não estiver no contexto, use seu conhecimento geral."
        )

        # 3. Montar mensagens para ChatGPT
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message}
        ]

        # 4. Gerar resposta
        response = client.chat.completions.create(
            model=CHAT_MODEL,
            messages=messages,
            temperature=0.5
        )

        return response.choices[0].message["content"]
