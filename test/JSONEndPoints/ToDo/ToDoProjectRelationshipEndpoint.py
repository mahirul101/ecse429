import requests
import pytest
import time
import subprocess
import psutil

BASE_URL = "http://localhost:4567"
TODOS_ENDPOINT = "/todos"
PROJECTS_ENDPOINT = "/projects"
PROJ_TODO_RELATIONSHIP = "tasks"
TODO_PROJ_RELATIONSHIP = "tasksof"
VALID_ID = 1
INVALID_ID = 40
JAR_PATH = "../../../runTodoManagerRestAPI-1.5.5.jar"

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
            response = requests.get(f"{BASE_URL}{TODOS_ENDPOINT}", timeout=2)
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
def test_head_projects_for_todo():
    todo_id = VALID_ID
    response = requests.head(f"{BASE_URL}{TODOS_ENDPOINT}/{todo_id}/{TODO_PROJ_RELATIONSHIP}")
    assert response.status_code == 200

def test_head_projects_for_nonexistent_todo():
    todo_id = INVALID_ID
    response = requests.head(f"{BASE_URL}{TODOS_ENDPOINT}/{todo_id}/{TODO_PROJ_RELATIONSHIP}")
    assert response.status_code == 200

def test_get_projects_for_todo():
    todo_id = 2
    response = requests.get(f"{BASE_URL}{TODOS_ENDPOINT}/{todo_id}/{TODO_PROJ_RELATIONSHIP}")
    expected = {
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
                ],
            },
        ]
    }
    assert response.status_code == 200
    assert response.json() == expected

def test_get_projects_for_nonexistent_todo():
    todo_id = INVALID_ID
    response = requests.get(f"{BASE_URL}{TODOS_ENDPOINT}/{todo_id}/{TODO_PROJ_RELATIONSHIP}")
    expected = {
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
                ],
            },
            {
                "id": "1",
                "title": "Office Work",
                "completed": "false",
                "active": "false",
                "description": "",
                "tasks": [
                    {"id": "2"},
                    {"id": "1"},
                ],
            },
        ]
    }
    assert response.status_code == 200
    assert response.json() == expected

def test_create_relationship_between_todo_and_project():
    todo_id = 2
    body = {"id": "1"}
    response = requests.post(f"{BASE_URL}{TODOS_ENDPOINT}/{todo_id}/{TODO_PROJ_RELATIONSHIP}", json=body)
    assert response.status_code == 201

    # Verify the relationship
    created_relationship = requests.get(f"{BASE_URL}{TODOS_ENDPOINT}/{todo_id}/{TODO_PROJ_RELATIONSHIP}")
    expected = {
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
                ],
            },
        ]
    }
    assert created_relationship.status_code == 200
    assert created_relationship.json() == expected

def test_create_relationship_with_nonexistent_todo():
    todo_id = INVALID_ID
    body = {"id": "1"}
    expected = {
        "errorMessages": [f"Could not find parent thing for relationship todos/{todo_id}/tasksof"],
    }
    response = requests.post(f"{BASE_URL}{TODOS_ENDPOINT}/{todo_id}/{TODO_PROJ_RELATIONSHIP}", json=body)
    assert response.status_code == 404
    assert response.json() == expected

def test_delete_relationship_between_todo_and_project():
    todo_id = 2
    proj_id = 1
    response = requests.delete(f"{BASE_URL}{TODOS_ENDPOINT}/{todo_id}/{TODO_PROJ_RELATIONSHIP}/{proj_id}")
    assert response.status_code == 200

    # Verify the deletion
    proj_relationships_of_todo = requests.get(f"{BASE_URL}{TODOS_ENDPOINT}/{todo_id}/{TODO_PROJ_RELATIONSHIP}")
    expected = {"projects": []}
    assert proj_relationships_of_todo.status_code == 200
    assert proj_relationships_of_todo.json() == expected

def test_delete_nonexistent_relationship_between_todo_and_project():
    todo_id = 2
    proj_id = 1
    response = requests.delete(f"{BASE_URL}{TODOS_ENDPOINT}/{todo_id}/{TODO_PROJ_RELATIONSHIP}/{proj_id}")
    assert response.status_code == 200

    second_attempt_response = requests.delete(f"{BASE_URL}{TODOS_ENDPOINT}/{todo_id}/{TODO_PROJ_RELATIONSHIP}/{proj_id}")
    expected = {
        "errorMessages": [f"Could not find any instances with todos/{todo_id}/tasksof/{proj_id}"],
    }
    assert second_attempt_response.status_code == 404
    assert second_attempt_response.json() == expected

def test_bidirectional_relationship_creation():
    body = {
        "title": "Important Errands and Tasks",
        "completed": False,
        "active": False,
        "description": "Need to be done this month",
    }

    # Create new project to make a relationship
    proj_created = requests.post(f"{BASE_URL}{PROJECTS_ENDPOINT}", json=body)
    assert proj_created.status_code == 201

    todo_id = 1
    proj_id_body = {"id": proj_created.json()["id"]}

    # Create todo-project relationship
    response = requests.post(f"{BASE_URL}{TODOS_ENDPOINT}/{todo_id}/{TODO_PROJ_RELATIONSHIP}", json=proj_id_body)
    assert response.status_code == 201

    # Verify todo-project side of the relationship
    created_relationship = requests.get(f"{BASE_URL}{TODOS_ENDPOINT}/{todo_id}/{TODO_PROJ_RELATIONSHIP}")
    expected = {
        "projects": [
            {
                "id": proj_id_body["id"],
                "title": "Important Errands and Tasks",
                "completed": "false",
                "active": "false",
                "description": "Need to be done this month",
                "tasks": [
                    {"id": "1"},
                ],
            },
            {
                "id": "1",
                "title": "Office Work",
                "completed": "false",
                "active": "false",
                "description": "",
                "tasks": [
                    {"id": "2"},
                    {"id": "1"},
                ],
            },
        ]
    }
    assert created_relationship.status_code == 200
    assert created_relationship.json() == expected

    # Verify project-todo side of the relationship
    proj_todo_relationships = requests.get(f"{BASE_URL}{PROJECTS_ENDPOINT}/{proj_created.json()['id']}/{PROJ_TODO_RELATIONSHIP}")
    expected_proj_todo_relationships = {
        "todos": [
            {
                "id": "1",
                "title": "scan paperwork",
                "doneStatus": "false",
                "description": "",
                "categories": [
                    {"id": "1"},
                ],
                "tasksof": [
                    {"id": proj_created.json()["id"]},
                    {"id": "1"},
                ],
            },
        ]
    }
    assert proj_todo_relationships.status_code == 200
    assert proj_todo_relationships.json() == expected_proj_todo_relationships

def test_bidirectional_relationship_deletion():
    todo_id = 1
    proj_id = 1

    # Delete existing todo-project relationship between todo with ID 1 and project with ID 1
    response = requests.delete(f"{BASE_URL}{TODOS_ENDPOINT}/{todo_id}/{TODO_PROJ_RELATIONSHIP}/{proj_id}")
    assert response.status_code == 200

    # Check deletion of relationship from todo side
    todo_proj_relationships = requests.get(f"{BASE_URL}{TODOS_ENDPOINT}/{todo_id}/{TODO_PROJ_RELATIONSHIP}")
    removed_project = {
        "id": "1",
        "title": "Office Work",
        "completed": "false",
        "active": "false",
        "description": "",
        "tasks": [
            {"id": "1"},
            {"id": "2"},
        ],
    }
    assert todo_proj_relationships.status_code == 200
    assert removed_project not in todo_proj_relationships.json()["projects"]

    # Check deletion of relationship from project side
    proj_todo_relationships = requests.get(f"{BASE_URL}{PROJECTS_ENDPOINT}/{proj_id}/{PROJ_TODO_RELATIONSHIP}")
    removed_todo = {
        "id": "1",
        "title": "scan paperwork",
        "doneStatus": "false",
        "description": "",
        "categories": [
            {"id": "1"},
        ],
        "tasksof": [
            {"id": "1"},
        ],
    }
    assert proj_todo_relationships.status_code == 200
    assert removed_todo not in proj_todo_relationships.json()["todos"]