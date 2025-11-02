from pydantic import BaseModel
from typing import Dict, Any

class GARMetrics(BaseModel):
    TCR: str
    GoalProgress: str
    Timeliness: str
    Quality: float

class GARResponse(BaseModel):
    employee_id: int
    employee_name: str
    metrics: GARMetrics
    GAR: float
    weights: Dict[str, float]
