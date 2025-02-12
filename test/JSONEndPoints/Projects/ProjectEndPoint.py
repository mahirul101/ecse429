import requests
import pytest
import time
import subprocess

BASE_URL = "http://localhost:4567"
PROJECTS_ENDPOINT = "/projects"
JAR_PATH = "C:/Users/dmytr/Desktop/SCHOOL/Winter_2025/ECSE_429/repo/runTodoManagerRestAPI-1.5.5.jar"

@pytest.fixture(scope="function", autouse=True)
def setup_and_teardown():
    # Start the Java application
    process = subprocess.Popen(["java", "-jar", JAR_PATH])

    # Wait for the server to be ready
    server_ready = False
    while not server_ready:
        try:
            requests.get(f"{BASE_URL}{PROJECTS_ENDPOINT}")
            server_ready = True
        except requests.exceptions.ConnectionError:
            time.sleep(1)

    yield

    # Shutdown the Java application
    requests.get(f"{BASE_URL}/shutdown")
    process.terminate()

def test_get_all_projects():
    response = requests.get(f"{BASE_URL}{PROJECTS_ENDPOINT}")
    expected = {
        "projects": [
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
    }
    assert response.status_code == 200
    assert response.json() == expected

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