# main.py
from flask import Flask
import threading
import time

app = Flask(__name__)

def run_autopilot_system():
    while True:
        print("Autopilot system running!")
        # Put your system's main automation logic here
        # Example: check for new tasks, generate products, etc.
        time.sleep(60)  # Run every 60 seconds

# Start the autopilot loop in a separate thread so Flask can serve the web endpoint
threading.Thread(target=run_autopilot_system, daemon=True).start()

# Minimal web endpoint to satisfy Render's port requirement
@app.route("/")
def home():
    return "Autopilot system is running!"

if __name__ == "__main__":
    # Render provides the PORT via environment variable
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
