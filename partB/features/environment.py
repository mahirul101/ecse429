import subprocess
import requests
import time
import psutil

BASE_URL = "http://localhost:4567"
JAR_PATH = "../../runTodoManagerRestAPI-1.5.5.jar"

def before_all(context):
    print("🚀 Starting the Todo Manager API...")
    # Start the Java application in the background
    context.process = subprocess.Popen(
        ["java", "-jar", JAR_PATH],
        stdout=subprocess.DEVNULL,  # Hide logs
        stderr=subprocess.DEVNULL
    )

    # Wait for the server to be ready
    max_retries = 5
    for attempt in range(max_retries):
        try:
            response = requests.get(f"{BASE_URL}/projects", timeout=2)
            if response.status_code == 200:
                break
        except requests.exceptions.ConnectionError:
            time.sleep(1)
    else:
        context.process.terminate()
        raise RuntimeError("Server failed to start.")

    print("✅ Todo Manager API is ready!")

def after_all(context):
    print("🛑 Shutting down the Todo Manager API...")
    # Gracefully shut down the server
    try:
        response = requests.get(f"{BASE_URL}/shutdown")
    except Exception:
        print("Server did not respond to shutdown request.")

    # Ensure the Java process is killed
    parent = psutil.Process(context.process.pid)
    for child in parent.children(recursive=True):
        child.kill()
    parent.kill()