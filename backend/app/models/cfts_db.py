"""CFTS Database models."""
from sqlalchemy import Column, String, DateTime, Integer
from sqlalchemy.sql import func
from ..db.database import Base


class CFTSRequirementDB(Base):
    __tablename__ = "cfts_requirements"

    id = Column(Integer, primary_key=True, index=True)
    cfts_id = Column(String, index=True)
    cfts_name = Column(String, default="") 
    req_id = Column(String, index=True) 
    source_id = Column(String, index=True)  
    description = Column(String, default="")  
    sr24_description = Column(String, default="") 
    melco_id = Column(String, default="") 
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())