from sqlalchemy.orm import Session
from typing import Tuple, List
from app.models.task import Task
from app.models.subtask import Subtask
from app.models.user import User
from app.models.gar_settings import GARSettings

def get_gar_weights_db(db: Session):
    settings = db.query(GARSettings).first()
    if not settings:
        return {"TCR":0.4, "GoalProgress":0.3, "Timeliness":0.2, "Quality":0.1}
    return {"TCR": settings.w_tcr, "GoalProgress": settings.w_goal, "Timeliness": settings.w_timeliness, "Quality": settings.w_quality}

def update_gar_weights_db(db: Session, w_tcr: float=None, w_goal: float=None, w_timeliness: float=None, w_quality: float=None):
    settings = db.query(GARSettings).first()
    if not settings:
        settings = GARSettings()
        db.add(settings)
    if w_tcr is not None: settings.w_tcr = w_tcr
    if w_goal is not None: settings.w_goal = w_goal
    if w_timeliness is not None: settings.w_timeliness = w_timeliness
    if w_quality is not None: settings.w_quality = w_quality
    db.commit()
    db.refresh(settings)
    return {"TCR": settings.w_tcr, "GoalProgress": settings.w_goal, "Timeliness": settings.w_timeliness, "Quality": settings.w_quality}

def _task_goal_progress(db: Session, task: Task) -> float:
    if task.is_quantitative:
        if task.goal_target and task.goal_target > 0:
            return min(float(task.goal_progress or 0) / float(task.goal_target), 1.0)
        return 0.0
    subtasks: List[Subtask] = db.query(Subtask).filter(Subtask.task_id == task.id).all()
    if not subtasks:
        if task.status == "completed": return 1.0
        if task.status == "in_progress": return 0.5
        return 0.0
    total_weight = sum(s.weight or 1.0 for s in subtasks)
    if total_weight == 0:
        return 0.0
    done_weight = sum((s.weight or 1.0) for s in subtasks if s.completed)
    return done_weight / total_weight

def calculate_gar(db: Session, employee_id: int, since_ts=None, until_ts=None) -> Tuple[dict, dict]:
    q = db.query(Task).filter(Task.assignee_id == employee_id)
    if since_ts:
        q = q.filter(Task.created_at >= since_ts)
    if until_ts:
        q = q.filter(Task.created_at <= until_ts)
    tasks = q.all()
    total = len(tasks)
    if total == 0:
        return {"GAR":0.0}, {"TCR":"0/0","GoalProgress":"0%","Timeliness":"0/0","Quality":0.0}

    completed_tasks = [t for t in tasks if t.status == "completed"]
    tcr_val = len(completed_tasks) / total

    progresses = [_task_goal_progress(db, t) for t in tasks]
    goal_progress_val = (sum(progresses) / len(progresses)) if progresses else 0.0

    timely_count = 0
    for t in completed_tasks:
        if t.deadline and t.completed_at:
            if t.completed_at <= t.deadline:
                timely_count += 1
        else:
            timely_count += 1
    timeliness_val = (timely_count / len(completed_tasks)) if completed_tasks else 0.0

    reviews = db.execute(
        "SELECT rating FROM manager_reviews mr JOIN tasks t ON mr.task_id = t.id WHERE t.assignee_id = :eid",
        {"eid": employee_id}
    ).fetchall()
    ratings = [r[0] for r in reviews if r[0] is not None]
    quality_val = (sum(ratings) / len(ratings)) if ratings else 0.0

    weights = get_gar_weights_db(db)

    quality_norm = quality_val / 5.0 if quality_val else 0.0

    gar_score = (tcr_val * weights["TCR"]) + (goal_progress_val * weights["GoalProgress"]) + (timeliness_val * weights["Timeliness"]) + (quality_norm * weights["Quality"])

    metrics = {
        "TCR": f"{len(completed_tasks)}/{total}",
        "GoalProgress": f"{round(goal_progress_val*100, 1)}%",
        "Timeliness": f"{timely_count}/{len(completed_tasks) if completed_tasks else 0}",
        "Quality": round(quality_val, 2)
    }
    return {"GAR": round(gar_score, 4)}, metrics, weights
