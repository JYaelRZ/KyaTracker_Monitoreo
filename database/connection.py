import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Supabase direct connection string provided by the user
# Database connection URL from environment variable or fallback (using port 6543 for Vercel/Serverless)
DATABASE_URL = os.environ.get("DATABASE_URL", "postgresql://postgres:Kyatracker8050@db.antefwqlngmqtavaamxz.supabase.co:6543/postgres?pgbouncer=true")

# Crear el engine
engine = create_engine(
    DATABASE_URL, 
    pool_pre_ping=True, 
    pool_size=10, 
    max_overflow=20
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
