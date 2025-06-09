import hashlib
import json
from datetime import datetime, timedelta
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from database.models import ResearchDatabase, Base
import logging

logger = logging.getLogger(__name__)
engine = create_engine("sqlite:///research_data.db")
Session = sessionmaker(bind=engine)
Base.metadata.create_all(engine)

class CacheManager:
    def __init__(self):
        self.session = Session()

    def get_cache_key(self, query_type: str, params: dict) -> str:
        key_str = f"{query_type}:{json.dumps(params, sort_keys=True)}"
        return hashlib.sha256(key_str.encode()).hexdigest()

    def get_cached_data(self, cache_key: str):
        try:
            record = self.session.query(ResearchDatabase).filter_by(query_hash=cache_key).first()
            if record and record.expires_at > datetime.utcnow():
                return json.loads(record.data)
            return None
        except Exception as e:
            logger.error(f"Cache read error: {e}")
            return None

    def cache_data(self, cache_key: str, query_type: str, data: dict, ttl_hours: int = 24):
        try:
            expiry = datetime.utcnow() + timedelta(hours=ttl_hours)
            record = ResearchDatabase(
                query_hash=cache_key,
                query_type=query_type,
                data=json.dumps(data),
                expires_at=expiry
            )
            self.session.merge(record)
            self.session.commit()
        except Exception as e:
            logger.error(f"Cache write error: {e}")
            self.session.rollback()