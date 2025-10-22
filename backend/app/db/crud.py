"""CRUD operations for CFTS requirements."""
from sqlalchemy.orm import Session
from typing import List, Optional
from ..models.cfts_db import CFTSRequirementDB
from ..models.requirement import CFTSRequirement


def create_cfts_requirement(db: Session, requirement: CFTSRequirement) -> CFTSRequirementDB:
    """Create a new CFTS requirement."""
    db_requirement = CFTSRequirementDB(
        cfts_id=requirement.cfts_id,
        cfts_name=requirement.cfts_name,
        req_id=requirement.req_id,
        source_id=requirement.source_id,
        description=requirement.description,
        sr24_description=requirement.sr24_description,
        melco_id=requirement.melco_id,
    )
    db.add(db_requirement)
    db.commit()
    db.refresh(db_requirement)
    return db_requirement


def get_cfts_requirements_by_cfts_id(db: Session, cfts_id: str) -> List[CFTSRequirementDB]:
    """Get all requirements for a specific CFTS ID (supports partial matching)."""
    # If user inputs just "CFTS016", search for all CFTS IDs that start with it
    if not cfts_id.endswith('-'):
        return db.query(CFTSRequirementDB).filter(
            CFTSRequirementDB.cfts_id.like(f"{cfts_id}%")
        ).all()
    else:
        # Exact match for full CFTS ID
        return db.query(CFTSRequirementDB).filter(CFTSRequirementDB.cfts_id == cfts_id).all()


def get_requirement_by_req_id(db: Session, req_id: str) -> Optional[CFTSRequirementDB]:
    """Get a specific requirement by Req.ID."""
    return db.query(CFTSRequirementDB).filter(CFTSRequirementDB.req_id == req_id).first()


def get_all_cfts_requirements(db: Session, skip: int = 0, limit: int = 1000) -> List[CFTSRequirementDB]:
    """Get all CFTS requirements."""
    return db.query(CFTSRequirementDB).offset(skip).limit(limit).all()


def bulk_create_cfts_requirements(db: Session, requirements: List[CFTSRequirement]) -> int:
    """Bulk create CFTS requirements (skip duplicates based on req_id)."""
    inserted_count = 0

    for req in requirements:
        # Check if requirement already exists by req_id
        existing = db.query(CFTSRequirementDB).filter(CFTSRequirementDB.req_id == req.req_id).first()

        if not existing:
            db_requirement = CFTSRequirementDB(
                cfts_id=req.cfts_id,
                cfts_name=req.cfts_name,
                req_id=req.req_id,
                source_id=req.source_id,
                description=req.description,
                sr24_description=req.sr24_description,
                melco_id=req.melco_id,
            )
            db.add(db_requirement)
            inserted_count += 1
        else:
            # Update existing record to keep latest data
            existing.cfts_name = req.cfts_name
            existing.source_id = req.source_id
            existing.description = req.description
            existing.sr24_description = req.sr24_description
            existing.melco_id = req.melco_id

    db.commit()
    return inserted_count
