import requests
import pytest
import time
import subprocess

BASE_URL = "http://localhost:4567"
PROJECTS_ENDPOINT = "/projects"
VALID_ID = 1
INVALID_ID = 20
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

def test_get_project_by_id():
    response = requests.get(f"{BASE_URL}{PROJECTS_ENDPOINT}/{VALID_ID}")
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

def test_get_nonexistent_project_by_id():
    response = requests.get(f"{BASE_URL}{PROJECTS_ENDPOINT}/{INVALID_ID}")
    expected = {
        "errorMessages": [f"Could not find an instance with projects/{INVALID_ID}"],
    }
    assert response.status_code == 404
    assert response.json() == expected

def test_head_project_by_id():
    response = requests.head(f"{BASE_URL}{PROJECTS_ENDPOINT}/{VALID_ID}")
    assert response.status_code == 200

def test_head_nonexistent_project_by_id():
    response = requests.head(f"{BASE_URL}{PROJECTS_ENDPOINT}/{INVALID_ID}")
    assert response.status_code == 404

def test_post_project_by_id():
    body = {
        "active": True,
        "description": "Meeting in progress",
    }
    response = requests.post(f"{BASE_URL}{PROJECTS_ENDPOINT}/{VALID_ID}", json=body)
    expected = {
        "id": "1",
        "title": "Office Work",
        "completed": "false",
        "active": "true",
        "description": "Meeting in progress",
        "tasks": [
            {"id": "1"},
            {"id": "2"},
        ],
    }
    assert response.status_code == 200
    assert response.json() == expected

def test_post_nonexistent_project_by_id():
    body = {
        "active": True,
        "description": "Meeting in progress",
    }
    response = requests.post(f"{BASE_URL}{PROJECTS_ENDPOINT}/{INVALID_ID}", json=body)
    expected = {
        "errorMessages": [f"No such project entity instance with GUID or ID {INVALID_ID} found"],
    }
    assert response.status_code == 404
    assert response.json() == expected

def test_put_project_by_id():
    body = {
        "title": "University Work",
        "active": True,
        "description": "Meeting in progress",
    }
    response = requests.put(f"{BASE_URL}{PROJECTS_ENDPOINT}/{VALID_ID}", json=body)
    expected = {
        "id": "1",
        "title": "University Work",
        "active": "true",
        "completed": "false",
        "description": "Meeting in progress",
    }
    assert response.status_code == 200
    assert response.json() == expected

def test_put_nonexistent_project_by_id():
    body = {
        "title": "University Work",
        "active": True,
        "description": "Meeting in progress",
    }
    response = requests.put(f"{BASE_URL}{PROJECTS_ENDPOINT}/{INVALID_ID}", json=body)
    expected = {
        "errorMessages": [f"Invalid GUID for {INVALID_ID} entity project"],
    }
    assert response.status_code == 404
    assert response.json() == expected

def test_delete_project_by_id():
    response = requests.delete(f"{BASE_URL}{PROJECTS_ENDPOINT}/{VALID_ID}")
    assert response.status_code == 200

def test_delete_nonexistent_project_by_id():
    response = requests.delete(f"{BASE_URL}{PROJECTS_ENDPOINT}/{INVALID_ID}")
    expected = {
        "errorMessages": [f"Could not find any instances with projects/{INVALID_ID}"],
    }
    assert response.status_code == 404
    assert response.json() == expected