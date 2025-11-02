from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional
from pydantic import BaseModel
from app.database import get_db
from app.auth import get_current_user
from app.models.user import UserRole
from app.schemas.analytics import GARResponse
from app.crud.gar import calculate_gar, update_gar_weights_db
from app.models.user import User

router = APIRouter(prefix="/api/analytics", tags=["analytics"])

@router.get("/employee/{employee_id}/gar", response_model=GARResponse)
def employee_gar(employee_id: int, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    if current_user.role not in [UserRole.admin, UserRole.hr, UserRole.manager] and current_user.id != employee_id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    gar_res, metrics, weights = calculate_gar(db, employee_id)
    user = db.query(User).filter(User.id == employee_id).first()
    return {
        "employee_id": employee_id,
        "employee_name": user.full_name if user else "Unknown",
        "metrics": metrics,
        "GAR": float(gar_res["GAR"]),
        "weights": weights
    }

class GARWeightsIn(BaseModel):
    TCR: Optional[float] = None
    GoalProgress: Optional[float] = None
    Timeliness: Optional[float] = None
    Quality: Optional[float] = None

@router.put("/gar-weights")
def update_gar_weights(payload: GARWeightsIn, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    if current_user.role != UserRole.admin:
        raise HTTPException(status_code=403, detail="Only admin can update weights")
    updated = update_gar_weights_db(
        db,
        w_tcr = payload.TCR,
        w_goal = payload.GoalProgress,
        w_timeliness = payload.Timeliness,
        w_quality = payload.Quality
    )
    return {"message": "updated", "weights": updated}
