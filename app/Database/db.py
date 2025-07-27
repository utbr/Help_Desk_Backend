from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError
from app.Core.config import settings


if not settings.DATABASE_URL:
    raise ValueError("A variável DATABASE_URL não está definida no .env")


engine = create_engine(
    str(settings.DATABASE_URL),
    pool_pre_ping=True,  
    future=True          
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    future=True
)
def get_db():
    db = SessionLocal()
    try:
        yield db
        db.commit()  
    except SQLAlchemyError:
        db.rollback() 
        raise
    finally:
        db.close()
