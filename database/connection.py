import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Supabase direct connection string provided by the user
# Database connection URL from environment variable or fallback
DATABASE_URL = os.environ.get("DATABASE_URL", "postgresql://postgres:Kyatracker8050@db.antefwqlngmqtavaamxz.supabase.co:5432/postgres")

# Crear el engine
engine = create_engine(
    DATABASE_URL, 
    pool_pre_ping=True, 
    pool_size=10, 
    max_overflow=20
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
