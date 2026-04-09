from app import create_app
from app.recovery import recover_stuck_tasks
import threading
import time

app = create_app()

def recovery_loop():
    while True:
        try:
            recover_stuck_tasks()
        except Exception as e:
            print(f"Recovery error: {str(e)}")
        time.sleep(20)

threading.Thread(target=recovery_loop, daemon=True).start()

if __name__ == "__main__":
    app.run(debug=True)