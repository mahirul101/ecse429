import requests
import pytest
import time
import subprocess

BASE_URL = "http://localhost:4567"
PROJECTS_ENDPOINT = "/projects"
TODOS_ENDPOINT = "/todos"
PROJ_TODO_RELATIONSHIP = "tasks"
TODO_PROJ_RELATIONSHIP = "projects"
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

@pytest.fixture(scope="function", autouse=True)
def create_task():
    body = {
        "title": "Gardening",
        "doneStatus": False,
        "description": "water the plants",
    }
    try:
        requests.post(f"{BASE_URL}{TODOS_ENDPOINT}", json=body)
    except requests.exceptions.RequestException:
        pass

def test_get_all_tasks_for_project():
    response = requests.get(f"{BASE_URL}{PROJECTS_ENDPOINT}/{VALID_ID}/{PROJ_TODO_RELATIONSHIP}")
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
            {
                "id": "2",
                "title": "file paperwork",
                "doneStatus": "false",
                "description": "",
                "tasksof": [
                    {"id": "1"},
                ],
            },
        ]
    }
    assert response.status_code == 200
    assert response.json() == expected

def test_get_tasks_for_nonexistent_project():
    response = requests.get(f"{BASE_URL}{PROJECTS_ENDPOINT}/{INVALID_ID}/{PROJ_TODO_RELATIONSHIP}")
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
            {
                "id": "2",
                "title": "file paperwork",
                "doneStatus": "false",
                "description": "",
                "tasksof": [
                    {"id": "1"},
                ],
            },
        ]
    }
    assert response.status_code == 200
    assert response.json() == expected

def test_head_tasks_for_project():
    response = requests.head(f"{BASE_URL}{PROJECTS_ENDPOINT}/{VALID_ID}/{PROJ_TODO_RELATIONSHIP}")
    assert response.status_code == 200

def test_head_tasks_for_nonexistent_project():
    response = requests.head(f"{BASE_URL}{PROJECTS_ENDPOINT}/{INVALID_ID}/{PROJ_TODO_RELATIONSHIP}")
    assert response.status_code == 200

def test_create_relationship_between_project_and_task():
    body = {"id": "2"}
    response = requests.post(f"{BASE_URL}{PROJECTS_ENDPOINT}/{VALID_ID}/{PROJ_TODO_RELATIONSHIP}", json=body)
    assert response.status_code == 201

    # Verifying that the relationship persists
    relationship = requests.get(f"{BASE_URL}{PROJECTS_ENDPOINT}/{VALID_ID}/{PROJ_TODO_RELATIONSHIP}")
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
            {
                "id": "2",
                "title": "file paperwork",
                "doneStatus": "false",
                "description": "",
                "tasksof": [
                    {"id": "1"},
                ],
            },
        ]
    }
    assert relationship.status_code == 200
    assert relationship.json() == expected

def test_create_relationship_with_nonexistent_project():
    body = {"id": "1"}
    expected = {
        "errorMessages": [f"Could not find parent thing for relationship projects/{INVALID_ID}/tasks"],
    }
    response = requests.post(f"{BASE_URL}{PROJECTS_ENDPOINT}/{INVALID_ID}/{PROJ_TODO_RELATIONSHIP}", json=body)
    assert response.status_code == 404
    assert response.json() == expected

def test_delete_relationship_between_project_and_task():
    todo_id = 2
    response = requests.delete(f"{BASE_URL}{PROJECTS_ENDPOINT}/{VALID_ID}/{PROJ_TODO_RELATIONSHIP}/{todo_id}")
    assert response.status_code == 200

    # Verify deletion through get request
    relationship = requests.get(f"{BASE_URL}{PROJECTS_ENDPOINT}/{VALID_ID}/{PROJ_TODO_RELATIONSHIP}")
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

def test_delete_nonexistent_relationship_between_project_and_task():
    todo_id = 20
    response = requests.delete(f"{BASE_URL}{PROJECTS_ENDPOINT}/{VALID_ID}/{PROJ_TODO_RELATIONSHIP}/{todo_id}")
    expected = {
        "errorMessages": [f"Could not find any instances with projects/{VALID_ID}/tasks/{todo_id}"],
    }
    assert response.status_code == 404
    assert response.json() == expected

def test_bidirectional_relationship_creation():
    body = {"id": "3"}
    response = requests.post(f"{BASE_URL}{PROJECTS_ENDPOINT}/{VALID_ID}/{PROJ_TODO_RELATIONSHIP}", json=body)
    assert response.status_code == 201

    # Check that the relationship exists from projects to tasks
    relationship = requests.get(f"{BASE_URL}{PROJECTS_ENDPOINT}/{VALID_ID}/{PROJ_TODO_RELATIONSHIP}")
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
            {
                "id": "2",
                "title": "file paperwork",
                "doneStatus": "false",
                "description": "",
                "tasksof": [
                    {"id": "1"},
                ],
            },
            {
                "id": "3",
                "title": "Gardening",
                "doneStatus": "false",
                "description": "water the plants",
                "tasksof": [
                    {"id": "1"},
                ],
            },
        ]
    }
    assert relationship.status_code == 200
    assert relationship.json() == expected

    # Check if task to projects relationship is created (bidirectionality)
    task_project_rel = requests.get(f"{BASE_URL}{TODOS_ENDPOINT}/{body['id']}/{TODO_PROJ_RELATIONSHIP}")
    expected_rel = {
        "projects": [
            {
                "id": "1",
                "title": "Office Work",
                "completed": "false",
                "active": "false",
                "description": "",
                "tasks": [
                    {"id": "2"},
                    {"id": "1"},
                    {"id": "3"},
                ],
            },
        ]
    }
    assert task_project_rel.status_code == 200
    assert task_project_rel.json() == expected_rel

def test_delete_bidirectional_relationship():
    todo_id = 2
    response = requests.delete(f"{BASE_URL}{PROJECTS_ENDPOINT}/{VALID_ID}/{PROJ_TODO_RELATIONSHIP}/{todo_id}")
    assert response.status_code == 200

    # Verify deletion through get request
    relationship = requests.get(f"{BASE_URL}{PROJECTS_ENDPOINT}/{VALID_ID}/{PROJ_TODO_RELATIONSHIP}")
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

    # Check if task to projects relationship is deleted (bidirectionality)
    task_project_rel = requests.get(f"{BASE_URL}{TODOS_ENDPOINT}/{todo_id}/{TODO_PROJ_RELATIONSHIP}")
    expected_proj = {"projects": []}
    assert task_project_rel.status_code == 200
    assert task_project_rel.json() == expected_proj