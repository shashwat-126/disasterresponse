from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.models.allocation import Allocation
from app.schemas.allocation import AllocationRead

router = APIRouter(prefix="/incidents", tags=["allocations"])


@router.get("/{incident_id}/allocation", response_model=AllocationRead)
def get_allocation(incident_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    allocation = (
        db.query(Allocation)
        .filter(Allocation.incident_id == incident_id)
        .order_by(Allocation.created_at.desc())
        .first()
    )
    if not allocation:
        raise HTTPException(status_code=404, detail="Allocation not found")
    return allocation
