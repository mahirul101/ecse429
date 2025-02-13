import requests
import pytest
import time
import subprocess
import psutil

BASE_URL = "http://localhost:4567"
PROJECTS_ENDPOINT = "/projects"
PROJ_TODO_RELATIONSHIP = "tasks"
VALID_ID = 1
INVALID_ID = 20
JAR_PATH = "runTodoManagerRestAPI-1.5.5.jar"

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
    parent = psutil.Process(process.pid)
    for child in parent.children(recursive=True):  # Kill child processes
        child.terminate()
    process.terminate()
    process.wait()

@pytest.fixture(scope="function", autouse=True)
def create_task():
    body = {
        "title": "Gardening",
        "doneStatus": False,
        "description": "water the plants",
    }
    try:
        requests.post(f"{BASE_URL}/todos", json=body)
    except requests.exceptions.RequestException:
        pass

def test_head_tasks_for_project():
    response = requests.head(f"{BASE_URL}{PROJECTS_ENDPOINT}/{VALID_ID}/{PROJ_TODO_RELATIONSHIP}", headers={"Content-Type": "application/xml"})
    assert response.status_code == 200

def test_head_tasks_for_nonexistent_project():
    response = requests.head(f"{BASE_URL}{PROJECTS_ENDPOINT}/{INVALID_ID}/{PROJ_TODO_RELATIONSHIP}", headers={"Content-Type": "application/xml"})
    assert response.status_code == 200

def test_post_project_todo_relationship():
    body = "<id>2</id>"
    headers = {"Content-Type": "application/xml"}
    response = requests.post(f"{BASE_URL}{PROJECTS_ENDPOINT}/{VALID_ID}/{PROJ_TODO_RELATIONSHIP}", data=body, headers=headers)
    expected = '{"errorMessages":["java.lang.IllegalStateException: Expected BEGIN_OBJECT but was STRING at line 1 column 1 path $"]}'
    assert response.status_code == 400
    assert response.text == expected

def test_post_project_todo_relationship_with_nonexistent_project():
    body = "<id>2</id>"
    headers = {"Content-Type": "application/xml"}
    response = requests.post(f"{BASE_URL}{PROJECTS_ENDPOINT}/{INVALID_ID}/{PROJ_TODO_RELATIONSHIP}", data=body, headers=headers)
    expected = '{"errorMessages":["java.lang.IllegalStateException: Expected BEGIN_OBJECT but was STRING at line 1 column 1 path $"]}'
    assert response.status_code == 400
    assert response.text == expected

def test_delete_project_todo_relationship():
    todo_id = 2
    response = requests.delete(f"{BASE_URL}{PROJECTS_ENDPOINT}/{VALID_ID}/{PROJ_TODO_RELATIONSHIP}/{todo_id}", headers={"Content-Type": "application/xml"})
    assert response.status_code == 200

    # Verify deletion through get request
    relationship = requests.get(f"{BASE_URL}{PROJECTS_ENDPOINT}/{VALID_ID}/{PROJ_TODO_RELATIONSHIP}", headers={"Content-Type": "application/xml"})
    expected = {
        "todos": [
            {
                "id": "1",
                "title": "scan paperwork",
                "doneStatus": "false",
                "description": "",
                "tasksof": [
                    {"id": "1"},
                ],
                "categories": [
                    {"id": "1"},
                ],
            },
        ]
    }
    assert relationship.status_code == 200
    assert relationship.json() == expected

def test_delete_nonexistent_project_todo_relationship():
    todo_id = 20
    response = requests.delete(f"{BASE_URL}{PROJECTS_ENDPOINT}/{VALID_ID}/{PROJ_TODO_RELATIONSHIP}/{todo_id}", headers={"Content-Type": "application/xml"})
    expected = {
        "errorMessages": [f"Could not find any instances with projects/{VALID_ID}/tasks/{todo_id}"],
    }
    assert response.status_code == 404
    assert response.json() == expected

def test_delete_project_todo_relationship_bidirectionality():
    todo_id = 2
    response = requests.delete(f"{BASE_URL}{PROJECTS_ENDPOINT}/{VALID_ID}/{PROJ_TODO_RELATIONSHIP}/{todo_id}", headers={"Content-Type": "application/xml"})
    assert response.status_code == 200

    # Verify deletion through get request
    relationship = requests.get(f"{BASE_URL}{PROJECTS_ENDPOINT}/{VALID_ID}/{PROJ_TODO_RELATIONSHIP}", headers={"Content-Type": "application/xml"})
    expected = {
        "todos": [
            {
                "id": "1",
                "title": "scan paperwork",
                "doneStatus": "false",
                "description": "",
                "tasksof": [
                    {"id": "1"},
                ],
                "categories": [
                    {"id": "1"},
                ],
            },
        ]
    }
    assert relationship.status_code == 200
    assert relationship.json() == expected

    # Check if todo=>projects relationship is deleted (bidirectionality)
    task_project_rel = requests.get(f"{BASE_URL}/todos/2/tasksof", headers={"Content-Type": "application/xml"})
    expected_proj = {
        "projects": [],
    }
    assert task_project_rel.status_code == 200
    assert task_project_rel.json() == expected_proj