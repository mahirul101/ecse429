import requests
import pytest
import time
import subprocess
import psutil

BASE_URL = "http://localhost:4567"
PROJECTS_ENDPOINT = "/projects"
JAR_PATH = "../../runTodoManagerRestAPI-1.5.5.jar"

@pytest.fixture(scope="function", autouse=True)
def setup_and_teardown():

    # Start the Java application in the background
    process = subprocess.Popen(
        ["java", "-jar", JAR_PATH],
        stdout=subprocess.DEVNULL,  # Hide logs
        stderr=subprocess.DEVNULL
    )

    # Wait for the server to be ready
    max_retries = 5
    for attempt in range(max_retries):
        try:
            response = requests.get(f"{BASE_URL}{PROJECTS_ENDPOINT}", timeout=2)
            if response.status_code == 200:
                break
        except requests.exceptions.ConnectionError:
            time.sleep(1)
    else:
        process.terminate()
        raise RuntimeError("Server failed to start.")

    # Tests are run here
    yield

    # Gracefully shut down the server
    try:
        requests.get(f"{BASE_URL}/shutdown")
    except Exception:
        print("Server did not respond to shutdown request.")

    # Ensure the Java process is killed
    parent = psutil.Process(process.pid)
    for child in parent.children(recursive=True):  # Kill child processes
        child.terminate()
    process.terminate()
    process.wait()

def test_head_projects():
    headers = {"Content-Type": "application/xml"}
    response = requests.head(f"{BASE_URL}{PROJECTS_ENDPOINT}", headers=headers)
    assert response.status_code == 200

def test_create_project_without_id():
    body = """
    <project>
        <active>false</active>
        <description>Meeting for 429 group</description>
        <completed>false</completed>
        <title>School</title>
    </project>
    """
    headers = {"Content-Type": "application/xml"}
    response = requests.post(f"{BASE_URL}{PROJECTS_ENDPOINT}", data=body, headers=headers)
    expected = {
        "id": "2",
        "title": "School",
        "completed": "false",
        "description": "Meeting for 429 group",
        "active": "false",
    }
    assert response.status_code == 201
    assert response.json() == expected

def test_create_project_with_invalid_active_status():
    body = """
    <project>
        <active>yes</active>
        <description>Write unit tests for 429</description>
        <completed>false</completed>
        <title>429 autoproj</title>
    </project>
    """
    headers = {"Content-Type": "application/xml"}
    response = requests.post(f"{BASE_URL}{PROJECTS_ENDPOINT}", data=body, headers=headers)
    expected = {
        "errorMessages": ["Failed Validation: active should be BOOLEAN"],
    }
    assert response.status_code == 400
    assert response.json() == expected