import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.pool import NullPool

# Supabase direct connection string provided by the user
# Database connection URL from environment variable or fallback (using port 6543 for Vercel/Serverless)
DATABASE_URL = os.environ.get("DATABASE_URL", "postgresql://postgres.antefwqlngmqtavaamxz:Kyatracker8050@aws-0-us-east-1.pooler.supabase.com:6543/postgres")

# Crear el engine – NullPool is required for serverless (Vercel) since
# persistent connection pools cannot be maintained across invocations.
engine = create_engine(
    DATABASE_URL,
    poolclass=NullPool,
    connect_args={
        "sslmode": "require",
        "connect_timeout": 10,
    },
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
