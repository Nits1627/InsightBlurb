from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, DateTime, Text

Base = declarative_base()

class ResearchDatabase(Base):
    __tablename__ = "research_cache"

    id = Column(Integer, primary_key=True)
    query_hash = Column(String(64), unique=True)
    query_type = Column(String(50))
    data = Column(Text)
    created_at = Column(DateTime, default=lambda: datetime.utcnow())
    expires_at = Column(DateTime)