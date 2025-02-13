import requests
import pytest
import time
import subprocess
import psutil

BASE_URL = "http://localhost:4567"
PROJECTS_ENDPOINT = "/projects"
CATEGORIES_ENDPOINT = "/categories"
JAR_PATH = "../../../runTodoManagerRestAPI-1.5.5.jar"

@pytest.fixture(scope="session", autouse=True)
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
            response = requests.get(f"{BASE_URL}{CATEGORIES_ENDPOINT}", timeout=2)
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
    try:
        parent = psutil.Process(process.pid)
        for child in parent.children(recursive=True):  # Kill child processes
            if child.is_running():
                child.terminate()
        if parent.is_running():
            parent.terminate()
        parent.wait()
    except psutil.NoSuchProcess:
        pass
    
def test_get_all_projects():
    response = requests.get(f"{BASE_URL}{PROJECTS_ENDPOINT}")
    expected_projects = [
        {
            "id": "1",
            "title": "Office Work",
            "completed": "false",
            "active": "false",
            "description": "",
            "tasks": [
                {"id": "1"},
                {"id": "2"},
            ],
        },
    ]
    assert response.status_code == 200
    response_projects = response.json().get("projects", [])
    # Sort tasks by ID before comparing
    for project in response_projects:
        project["tasks"].sort(key=lambda x: x["id"])
    for project in expected_projects:
        project["tasks"].sort(key=lambda x: x["id"])
    assert response_projects == expected_projects

def test_head_projects():
    response = requests.head(f"{BASE_URL}{PROJECTS_ENDPOINT}")
    assert response.status_code == 200

def test_create_project_without_id():
    body = {
        "title": "School",
        "description": "Meeting for 429 group",
    }
    response = requests.post(f"{BASE_URL}{PROJECTS_ENDPOINT}", json=body)
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
    body = {
        "completed": False,
        "title": "429 autoproj",
        "description": "Write unit tests for 429",
        "active": "yes",
    }
    response = requests.post(f"{BASE_URL}{PROJECTS_ENDPOINT}", json=body)
    expected = {
        "errorMessages": ["Failed Validation: active should be BOOLEAN"],
    }
    assert response.status_code == 400
    assert response.json() == expected