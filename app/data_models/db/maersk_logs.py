from datetime import datetime

from sqlalchemy import Column, DateTime, Integer, String
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class MaerskRatingLog(Base):
    __tablename__ = "maersk_rating_log"
    __table_args__ = {"schema": "maersk_copilot"}

    id = Column(Integer, primary_key=True, index=True)
    endpoint = Column(String, nullable=False)
    request_data = Column(JSON, nullable=False)
    response_data = Column(JSON, nullable=False)
    original_response = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class MaerskShipmentLog(Base):
    __tablename__ = "maersk_shipment_log"
    __table_args__ = {"schema": "maersk_copilot"}

    id = Column(Integer, primary_key=True, index=True)
    endpoint = Column(String, nullable=False)
    request_data = Column(JSON, nullable=False)
    response_data = Column(JSON, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)


class MaerskLabelLog(Base):
    __tablename__ = "maersk_label_log"
    __table_args__ = {"schema": "maersk_copilot"}

    id = Column(Integer, primary_key=True, index=True)
    endpoint = Column(String, nullable=False)
    request_data = Column(JSON, nullable=False)
    response_data = Column(JSON, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
