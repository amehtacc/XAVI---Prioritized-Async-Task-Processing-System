from app.celery_app import celery
from app.db import SessionLocal
from app.models import Task
import random
import time

@celery.task(bind=True)
def process_task(self, task_id):
    db = SessionLocal()

    try:
        task = db.query(Task).filter(
            Task.id == task_id,
            Task.status == "PENDING"
        ).with_for_update().first()

        if not task:
            return

        if task.status == "SUCCESS":
            return

        print(f"Processing task {task.id} with priority {task.priority}")

        task.status = "PROCESSING"
        db.commit()

        time.sleep(2)

        if random.random() < 0.3:
            task.retry_count += 1

            if task.retry_count <= 3:
                print(f"Retrying task {task.id}, attempt {task.retry_count}")

                task.status = "PENDING"
                db.commit()

                process_task.apply_async(
                    args=[task.id],
                    queue=task.priority.lower()
                )
            else:
                print(f"Task {task.id} failed after max retries")

                task.status = "FAILED"
                db.commit()

            return

        print(f"Task {task.id} completed successfully")

        task.status = "SUCCESS"
        db.commit()

    except Exception as e:
        print(f"Error processing task {task_id}: {str(e)}")

    finally:
        db.close()