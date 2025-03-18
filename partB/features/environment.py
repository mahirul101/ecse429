import subprocess
import requests
import time
import psutil

BASE_URL = "http://localhost:4567"
JAR_PATH = "../../runTodoManagerRestAPI-1.5.5.jar"

def before_all(context):
    print("🚀 Checking if Todo Manager API is started...")
    # Start the Java application in the background
    # context.process = subprocess.Popen(
    #     ["java", "-jar", JAR_PATH],
    #     stdout=subprocess.DEVNULL,  # Hide logs
    #     stderr=subprocess.DEVNULL
    # )

    # Wait for the server to be ready
    max_retries = 2
    for attempt in range(max_retries):
        try:
            response = requests.get(f"{BASE_URL}/projects", timeout=2)
            if response.status_code == 200:
                break
        except requests.exceptions.ConnectionError:
            time.sleep(1)
    else:
        raise RuntimeError("Server not started.")

    print("✅ Todo Manager API is ready!")

def after_all(context):
    # Gracefully shut down the server
    try: 
      print("🛑 Shutting down the Todo Manager API...")
      response = requests.get(f"{BASE_URL}/shutdown")
    except requests.exceptions.ConnectionError:
      pass
