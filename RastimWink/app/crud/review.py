from sqlalchemy.orm import Session
from app.models.review import EmployeeComment, ManagerReview
from app.schemas.review import EmployeeCommentCreate, ManagerReviewCreate
from app.models.task import Task

def create_employee_comment(db: Session, comment: EmployeeCommentCreate, employee_id: int):
    db_comment = EmployeeComment(**comment.dict(), employee_id = employee_id)
    db.add(db_comment)

    task = db.query(Task).filter(Task.id == comment.task_id).first()
    if task:
        task.comments_received += 1
    
    db.commit()
    db.refresh(db_comment)
    return db_comment

def create_manager_review(db: Session, review: ManagerReviewCreate, manager_id: int):
    db_review = ManagerReview(**review.dict(), manager_id = manager_id)
    db.add(db_review)
    db.commit()
    db.refresh(db_review)
    return db_review

def get_task_comments(db: Session, task_id: int):
    comments = db.query(EmployeeComment).filter(EmployeeComment.task_id == task_id).all()
    task = db.query(Task).filter(Task.id == task_id).first()

    return {
        "total_comments": len(comments),
        "required_comments": task.min_comments if task else 5,
        "completion_percentage": round((len(comments) / (task.min_comments if task else 5)) * 100, 2) if task else 0
    }