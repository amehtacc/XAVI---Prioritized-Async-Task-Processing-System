from app.db import SessionLocal
from app.models import Task
from app.tasks import process_task
from datetime import datetime, timedelta

def recover_stuck_tasks():
    db = SessionLocal()

    try:
        timeout = datetime.utcnow() - timedelta(seconds=30)

        stuck_tasks = db.query(Task).filter(
            Task.status == "PROCESSING",
            Task.updated_at < timeout
        ).all()

        for task in stuck_tasks:
            print(f"Recovering stuck task {task.id}")

            task.status = "PENDING"
            db.commit()

            process_task.apply_async(
                args=[task.id],
                queue=task.priority.lower()
            )

    finally:
        db.close()