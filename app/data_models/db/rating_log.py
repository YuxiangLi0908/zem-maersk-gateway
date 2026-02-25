from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.postgresql import JSON
from datetime import datetime

Base = declarative_base()

class MaerskRatingLog(Base):
    __tablename__ = "maersk_rating_log"

    id = Column(Integer, primary_key=True, index=True)
    endpoint = Column(String, nullable=False)
    request_data = Column(JSON, nullable=False)
    response_data = Column(JSON, nullable=False)
    original_response = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
