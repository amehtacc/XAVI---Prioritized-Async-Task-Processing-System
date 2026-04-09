# 🚀 Prioritized Async Task Processing System

This project implements a prioritized asynchronous task processing system using **Flask, PostgreSQL, Redis, and Celery**.

It supports task submission, tracking, priority-based execution, retries, concurrency control, and failure recovery.



## 🧠 Architecture Overview
Client → Flask API → PostgreSQL (Task Storage)
↓
Redis (Queue)
↓
Celery Workers
↓
Task Processing & Updates




## ⚙️ Features

- Submit tasks with priority (HIGH / MEDIUM / LOW)
- Asynchronous task processing using Celery
- Priority-based execution using multiple queues
- Retry mechanism with failure simulation (~30%)
- Concurrency-safe processing (no duplicate execution)
- Worker crash recovery (self-healing system)
- Task lifecycle tracking



## 📦 Tech Stack

- **Backend:** Flask
- **Database:** PostgreSQL
- **Queue/Broker:** Redis
- **Worker System:** Celery



## 📌 API Endpoints

### 1. Submit Task
POST /tasks
**Body:**
```json
{
  "payload": {"data": "example"},
  "priority": "HIGH"
}
```

### 2. Get Task Status
```
GET /tasks/:id
```

### 3. List Tasks
```
GET /tasks?status=&priority=
```


## 🧱 Task Schema
* id (UUID)
* payload (JSON)
* priority (HIGH / MEDIUM / LOW)
* status (PENDING / PROCESSING / SUCCESS / FAILED)
* retry_count
* created_at
* updated_at


## 🔥 Queue Design

The system uses multiple queues to enforce priority:

* high
* medium
* low

Tasks are routed to queues based on their priority.

Celery workers are configured as:
```
celery -A app.celery_app.celery worker -Q high,medium,low
```
This ensures:

* HIGH priority tasks are always processed first
* MEDIUM only after HIGH is empty
* LOW only after both are empty

This avoids naive database sorting and ensures true priority execution.


## ⚡ Priority Handling

Priority is enforced using queue-level separation, not database sorting.

* Each task is pushed to its respective queue
* Workers consume queues in strict order: high → medium → low

This guarantees correct execution order even with multiple workers.

## 🔒 Concurrency Strategy

To prevent duplicate processing:

* Row-level locking is used via SELECT FOR UPDATE
* Task is updated from PENDING → PROCESSING atomically
* Only one worker can acquire a task

This ensures:

* No race conditions
* No task processed twice simultaneously

## 🔁 Retry Mechanism
* ~30% failure is simulated using randomness
* Each task can retry up to 3 times
* Retry logic:
```
If failure → increment retry_count
If retry_count ≤ 3 → requeue task
Else → mark as FAILED
```

Retries are pushed back to the same priority queue, preserving execution order.

## 🧠 Idempotency

Idempotency is ensured by:

* Checking task status before execution
* Skipping execution if task is already SUCCESS

This prevents duplicate processing in retry scenarios.

## ♻️ Worker Crash Recovery

If a worker crashes:

* Task may remain in PROCESSING
* A recovery mechanism detects stuck tasks using updated_at timestamp

Recovery logic:

* If task is in PROCESSING for too long → reset to PENDING
* Requeue task based on priority

This ensures the system is self-healing.

## 🔁 At-least-once Processing

The system guarantees at-least-once execution:

* Tasks are stored in the database before processing
* Failed or interrupted tasks are retried
* Recovery mechanism ensures no task is lost


## ⚖️ Trade-offs
Simplicity vs Scalability
* Used Redis + Celery for simplicity
* Kafka/RabbitMQ would provide better scalability but increase complexity

Thread-based Recovery
* Used background thread for recovery (simple)
* In production, Celery Beat or external schedulers are preferred

Database Locking
* Strong consistency using row-level locks
* May impact performance under very high load


## ▶️ Running the Project
Start Redis
```
docker run -d -p 6379:6379 redis
```
Start Worker
```
celery -A app.celery_app.celery worker -Q high,medium,low --loglevel=info
```
Run Backend
```
python run.py
```


## 🧠 Summary

This system demonstrates:

* Asynchronous processing
* Priority-based execution
* Concurrency-safe design
* Failure handling and retries
* Self-healing architecture

It is designed to mimic real-world distributed task processing systems.