from sqlalchemy.orm import Session
from app.models.stats import EmployeeStats
from app.models.user import User
from app.models.task import Task
from app.models.review import ManagerReview
from datetime import datetime

def get_employee_stats(db: Session, employee_id: int):
    return db.query(EmployeeStats).filter(EmployeeStats.employee_id == employee_id).first()

def update_employee_stats(db: Session, employee_id: int, task_rating: float = None):
    stats = get_employee_stats(db, employee_id)
    if not stats:
        stats = EmployeeStats(employee_id=employee_id, tasks_completed=0, average_rating=0.0)
        db.add(stats)
    if task_rating is not None:
        total_reviews = getattr(stats, "review_count", 0)
        current_avg = getattr(stats, "average_rating", 0.0) or 0.0
        new_total = total_reviews + 1
        new_avg = (current_avg * total_reviews + task_rating) / new_total
        stats.rating_count = new_total
        stats.average_rating = new_avg
    db.commit()
    db.refresh(stats)
    return stats

def get_employee_detailed_stats(db: Session, employee_id: int):
    employee = db.query(User).filter(User.id == employee_id).first()
    if not employee:
        return None
    tasks_completed = db.query(Task).filter(Task.assignee_id == employee_id, Task.status == "completed").count()
    reviews = (
        db.query(ManagerReview)
        .join(Task)
        .filter(Task.assignee_id == employee_id)
        .order_by(ManagerReview.created_at.desc())
        .limit(5)
        .all()
    )
    ratings = [r.rating for r in reviews if r.rating is not None]
    avg_rating = round(sum(ratings) / len(ratings), 2) if ratings else None
    return {
        "employee_id": employee_id,
        "employee_name": employee.full_name,
        "tasks_completed": tasks_completed,
        "average_rating": avg_rating,
        "recent_reviews": [
            {
                "task_id": r.task_id,
                "rating": r.rating,
                "comment": r.comment,
                "created_at": r.created_at
            } for r in reviews
        ]
    }

def get_company_stats(db: Session):
    total_employees = db.query(User).count()
    total_tasks_completed = db.query(Task).filter(Task.status == "completed").count()
    total_reviews = db.query(ManagerReview).count()
    return {
        "total_employees": total_employees,
        "total_tasks_completed": total_tasks_completed,
        "manager_reviews_total": total_reviews
    }
