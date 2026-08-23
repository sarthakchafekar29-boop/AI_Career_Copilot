from sqlalchemy import Column, Integer, String, Text, ForeignKey 
from sqlalchemy.orm import relationship

from db import Base, engine


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(100), unique=True, nullable=False)
    password = Column(String(100), nullable=False)

    reports = relationship("Report", back_populates="user")


class Report(Base):
    __tablename__ = "reports"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    resume_text = Column(Text)
    result = Column(Text)

    user = relationship("User", back_populates="reports")


# Create all tables
Base.metadata.create_all(bind=engine)

print("Tables created successfully!")