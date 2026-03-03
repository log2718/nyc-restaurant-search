import os
from sqlalchemy import create_engine, Column, Integer, String, Text, Boolean, text
from sqlalchemy.orm import declarative_base, sessionmaker
from pgvector.sqlalchemy import Vector
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+psycopg://myuser:mypassword@localhost:5432/vectordb")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

class Restaurant(Base):
    __tablename__ = "restaurants"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    category = Column(String)
    review_comment = Column(Text)
    popular_food = Column(String)
    online_order = Column(Boolean)
    number_of_reviews = Column(Integer)
    embedding = Column(Vector(384)) # sentence-transformers/all-MiniLM-L6-v2 uses 384 dimensions

def init_db():
    # Install pgvector extension within Postgres
    with engine.begin() as conn: # engine.begin() auto-commits
        conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
    Base.metadata.create_all(bind=engine)
