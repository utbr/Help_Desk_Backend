from sqlalchemy import (
    Column, Integer, String, Text, Boolean, TIMESTAMP, ForeignKey
)
from sqlalchemy.orm import relationship, declarative_base
from sqlalchemy.sql import func
from pgvector.sqlalchemy import Vector 

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    __table_args__ = {"schema": "help_desk"}

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    password_hash = Column(Text, nullable=False)
    role = Column(String(20), nullable=False, default="user")  # user, admin, agent
    is_active = Column(Boolean, default=True)
    created_at = Column(TIMESTAMP, server_default=func.now())

    tickets_created = relationship("Ticket", back_populates="user", foreign_keys="Ticket.user_id")
    tickets_assigned = relationship("Ticket", back_populates="assigned_to_user", foreign_keys="Ticket.assigned_to")


class TicketCategory(Base):
    __tablename__ = "ticket_categories"
    __table_args__ = {"schema": "help_desk"}

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, nullable=False)

    tickets = relationship("Ticket", back_populates="category")
    contexts = relationship("Context", back_populates="category", cascade="all, delete")


class Ticket(Base):
    __tablename__ = "tickets"
    __table_args__ = {"schema": "help_desk"}

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(150), nullable=False)
    description = Column(Text, nullable=False)
    status = Column(String(20), default="open")
    priority = Column(String(20), default="medium")
    user_id = Column(Integer, ForeignKey("help_desk.users.id"))
    category_id = Column(Integer, ForeignKey("help_desk.ticket_categories.id"))
    assigned_to = Column(Integer, ForeignKey("help_desk.users.id"), nullable=True)
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    user = relationship("User", back_populates="tickets_created", foreign_keys=[user_id])
    assigned_to_user = relationship("User", back_populates="tickets_assigned", foreign_keys=[assigned_to])
    category = relationship("TicketCategory", back_populates="tickets")
    messages = relationship("TicketMessage", back_populates="ticket", cascade="all, delete")
    history = relationship("TicketHistory", back_populates="ticket", cascade="all, delete")


class TicketMessage(Base):
    __tablename__ = "ticket_messages"
    __table_args__ = {"schema": "help_desk"}

    id = Column(Integer, primary_key=True)
    ticket_id = Column(Integer, ForeignKey("help_desk.tickets.id", ondelete="CASCADE"))
    sender_id = Column(Integer, ForeignKey("help_desk.users.id"))
    message = Column(Text, nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.now())

    ticket = relationship("Ticket", back_populates="messages")


class TicketHistory(Base):
    __tablename__ = "ticket_history"
    __table_args__ = {"schema": "help_desk"}

    id = Column(Integer, primary_key=True)
    ticket_id = Column(Integer, ForeignKey("help_desk.tickets.id", ondelete="CASCADE"))
    action = Column(Text, nullable=False)
    performed_by = Column(Integer, ForeignKey("help_desk.users.id"))
    created_at = Column(TIMESTAMP, server_default=func.now())

    ticket = relationship("Ticket", back_populates="history")


class Context(Base):
    __tablename__ = "context"
    __table_args__ = {"schema": "help_desk"}

    id = Column(Integer, primary_key=True)
    category_id = Column(Integer, ForeignKey("help_desk.ticket_categories.id", ondelete="CASCADE"))
    chunk_index = Column(Integer, nullable=False)
    chunk_text = Column(Text, nullable=False)
    embedding = Column(Vector(1536), nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.now())

    category = relationship("TicketCategory", back_populates="contexts")
