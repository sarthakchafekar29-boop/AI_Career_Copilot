from sqlalchemy import create_engine # type: ignore
from sqlalchemy.orm import declarative_base, sessionmaker 

DATABASE_URL = "postgresql+psycopg2://postgres:samruddhi@localhost:5432/ai_career_copilot"

engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()