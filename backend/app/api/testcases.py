"""Test case API endpoints."""
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..db.database import get_db
from ..models.testcase import TestCaseDB, TestCaseResponse

router = APIRouter(prefix="/testcases", tags=["testcases"])


def _db_to_response(record: TestCaseDB) -> TestCaseResponse:
    """Convert SQLAlchemy model to API response model."""
    return TestCaseResponse(
        feature_id=record.feature_id,
        source=record.source or "",
        title=record.title or "",
        section=record.section or "",
        test_item_en=record.test_item_en or "",
        precondition_procedure_jp=record.precondition_procedure_jp or "",
        criteria_jp=record.criteria_jp or "",
    )


@router.get(
    "/by-feature-id/{feature_id}",
    response_model=List[TestCaseResponse],
    summary="依 Feature ID 取得對應測試案例",
)
def get_testcases_by_feature_id(feature_id: str, db: Session = Depends(get_db)) -> List[TestCaseResponse]:
    """Return all test cases that match the specified feature (Melco) ID."""
    records = (
        db.query(TestCaseDB)
        .filter(TestCaseDB.feature_id == feature_id)
        .order_by(TestCaseDB.id.asc())
        .all()
    )

    if not records:
        raise HTTPException(status_code=404, detail="Test cases not found")

    return [_db_to_response(record) for record in records]
