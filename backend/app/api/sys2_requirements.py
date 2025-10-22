"""SYS.2 requirement API endpoints."""
from typing import Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session

from ..db.database import get_db
from ..models.cfts_db import CFTSRequirementDB
from ..models.sys2_requirement import SYS2RequirementDB, SYS2Requirement

router = APIRouter(prefix="/sys2", tags=["sys2"])


class SYS2AvailabilityResponse(BaseModel):
    """Response model for Melco ID availability lookups."""
    available_ids: List[str]


def _build_cfts_lookup(db: Session, cfts_ids: List[str]) -> Dict[str, str]:
    """Fetch distinct CFTS names for the provided IDs."""
    if not cfts_ids:
        return {}

    rows = (
        db.query(CFTSRequirementDB.cfts_id, CFTSRequirementDB.cfts_name)
        .filter(CFTSRequirementDB.cfts_id.in_(cfts_ids))
        .distinct()
        .all()
    )
    return {cfts_id: cfts_name or "" for cfts_id, cfts_name in rows}


def _to_pydantic(record: SYS2RequirementDB, cfts_lookup: Dict[str, str]) -> SYS2Requirement:
    """Convert DB model to Pydantic model, enriching CFTS name when missing."""
    requirement = SYS2Requirement.model_validate(record, from_attributes=True)

    if requirement.cfts_id and not requirement.cfts_name:
        requirement.cfts_name = cfts_lookup.get(requirement.cfts_id, "")

    return requirement


@router.get(
    "/requirement/{melco_id}",
    response_model=List[SYS2Requirement],
    summary="取得指定 Melco ID 的 SYS.2 要件資料",
)
def get_sys2_by_melco_id(melco_id: str, db: Session = Depends(get_db)) -> List[SYS2Requirement]:
    """Return SYS.2 requirements associated with a specific Melco ID."""
    records = (
        db.query(SYS2RequirementDB)
        .filter(SYS2RequirementDB.melco_id == melco_id)
        .order_by(SYS2RequirementDB.id.asc())
        .all()
    )

    if not records:
        raise HTTPException(status_code=404, detail="SYS.2 requirement not found")

    cfts_lookup = _build_cfts_lookup(
        db, [record.cfts_id for record in records if record.cfts_id]
    )

    return [_to_pydantic(record, cfts_lookup) for record in records]


@router.get(
    "/search",
    response_model=List[SYS2Requirement],
    summary="依條件搜尋 SYS.2 要件",
)
def search_sys2_requirements(
    cfts_id: Optional[str] = Query(default=None, description="CFTS 編號，可模糊搜尋"),
    melco_id: Optional[str] = Query(default=None, description="Melco ID，可模糊搜尋"),
    limit: int = Query(default=50, ge=1, le=200, description="回傳筆數上限"),
    db: Session = Depends(get_db),
) -> List[SYS2Requirement]:
    """Search SYS.2 requirements by CFTS ID or Melco ID."""
    query = db.query(SYS2RequirementDB)

    if cfts_id:
        query = query.filter(SYS2RequirementDB.cfts_id.ilike(f"{cfts_id}%"))

    if melco_id:
        query = query.filter(SYS2RequirementDB.melco_id.ilike(f"{melco_id}%"))

    records = query.order_by(SYS2RequirementDB.melco_id.asc()).limit(limit).all()

    if not records:
        return []

    cfts_lookup = _build_cfts_lookup(
        db, [record.cfts_id for record in records if record.cfts_id]
    )

    return [_to_pydantic(record, cfts_lookup) for record in records]


@router.get(
    "/availability",
    response_model=SYS2AvailabilityResponse,
    summary="檢查多個 Melco ID 是否存在 SYS.2 資料",
)
def check_sys2_availability(
    ids: str = Query(
        ...,
        description="以逗號分隔的 Melco ID 列表，例如 'PSCFTS016-1,PSCFTS017-2'",
        min_length=1,
    ),
    db: Session = Depends(get_db),
) -> SYS2AvailabilityResponse:
    """Batch check which Melco IDs have SYS.2 requirements."""
    # 解析輸入，過濾空白與重複
    raw_ids = [item.strip() for item in ids.split(",") if item.strip()]
    unique_ids = list(dict.fromkeys(raw_ids))  # 保留順序且去重

    if not unique_ids:
        return SYS2AvailabilityResponse(available_ids=[])

    rows = (
        db.query(SYS2RequirementDB.melco_id)
        .filter(SYS2RequirementDB.melco_id.in_(unique_ids))
        .distinct()
        .all()
    )

    available = [melco_id for (melco_id,) in rows]
    return SYS2AvailabilityResponse(available_ids=available)
