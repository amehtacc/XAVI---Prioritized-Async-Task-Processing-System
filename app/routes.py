from flask import Blueprint, request, jsonify
from app.db import SessionLocal
from app.models import Task
from app.tasks import process_task

routes = Blueprint("routes", __name__)

# Create Task
@routes.route("/tasks", methods=["POST"])
def create_task():
    db = SessionLocal()

    data = request.json

    task = Task(
        payload=data.get("payload"),
        priority=data.get("priority")
    )

    db.add(task)
    db.commit()
    db.refresh(task)

    queue_name = task.priority.lower()

    process_task.apply_async(args=[task.id], queue=queue_name)

    return jsonify({"id": task.id, "status": task.status})


# Get Task
@routes.route("/tasks/<task_id>", methods=["GET"])
def get_task(task_id):
    db = SessionLocal()

    task = db.query(Task).filter(Task.id == task_id).first()

    if not task:
        return jsonify({"error": "Task not found"}), 404

    return jsonify({
        "id": task.id,
        "status": task.status,
        "retry_count": task.retry_count
    })


# List Tasks
@routes.route("/tasks", methods=["GET"])
def list_tasks():
    db = SessionLocal()

    status = request.args.get("status")
    priority = request.args.get("priority")

    query = db.query(Task)

    if status:
        query = query.filter(Task.status == status)

    if priority:
        query = query.filter(Task.priority == priority)

    tasks = query.all()

    return jsonify([{
        "id": t.id,
        "status": t.status,
        "priority": t.priority
    } for t in tasks])