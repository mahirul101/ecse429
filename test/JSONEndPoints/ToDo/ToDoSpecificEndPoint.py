import requests
import pytest
import time
import subprocess

BASE_URL = "http://localhost:4567"
TODOS_ENDPOINT = "/todos"
VALID_ID = 1
INVALID_ID = 45
JAR_PATH = "C:/Users/dmytr/Desktop/SCHOOL/Winter_2025/ECSE_429/repo/runTodoManagerRestAPI-1.5.5.jar"

@pytest.fixture(scope="function", autouse=True)
def setup_and_teardown():
    # Start the Java application
    process = subprocess.Popen(["java", "-jar", JAR_PATH])
    
    # Wait for the server to be ready
    server_ready = False
    while not server_ready:
        try:
            requests.get(f"{BASE_URL}{TODOS_ENDPOINT}")
            server_ready = True
        except requests.exceptions.ConnectionError:
            time.sleep(1)

    yield

    # Shutdown the Java application
    requests.get(f"{BASE_URL}/shutdown")
    process.terminate()

def test_get_todo_by_id():
    todo_id = VALID_ID
    response = requests.get(f"{BASE_URL}{TODOS_ENDPOINT}/{todo_id}")
    expected = {
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
                    {"id": "1"},
                ],
            },
        ]
    }
    assert response.status_code == 200
    assert response.json() == expected

def test_get_nonexistent_todo_by_id():
    todo_id = INVALID_ID
    response = requests.get(f"{BASE_URL}{TODOS_ENDPOINT}/{todo_id}")
    expected = {
        "errorMessages": [f"Could not find an instance with todos/{todo_id}"],
    }
    assert response.status_code == 404
    assert response.json() == expected

def test_create_todo():
    body = {
        "title": "Wash Dishes",
        "doneStatus": False,
        "description": "Home Chore to be done",
    }
    response = requests.post(f"{BASE_URL}{TODOS_ENDPOINT}", json=body)
    expected = {
        "id": "3",
        "title": "Wash Dishes",
        "doneStatus": "false",
        "description": "Home Chore to be done",
    }
    assert response.status_code == 201
    assert response.json() == expected

def test_update_todo_by_id():
    todo_id = VALID_ID
    body = {
        "doneStatus": True,
        "description": "all paperwork scanned",
    }
    response = requests.post(f"{BASE_URL}{TODOS_ENDPOINT}/{todo_id}", json=body)
    expected = {
        "id": "1",
        "title": "scan paperwork",
        "doneStatus": "true",
        "description": "all paperwork scanned",
        "categories": [
            {"id": "1"},
        ],
        "tasksof": [
            {"id": "1"},
        ],
    }
    assert response.status_code == 200
    assert response.json() == expected

def test_update_nonexistent_todo_by_id():
    todo_id = INVALID_ID
    body = {
        "doneStatus": True,
        "description": "all paperwork scanned",
    }
    response = requests.post(f"{BASE_URL}{TODOS_ENDPOINT}/{todo_id}", json=body)
    expected = {
        "errorMessages": [f"No such todo entity instance with GUID or ID {todo_id} found"],
    }
    assert response.status_code == 404
    assert response.json() == expected

def test_head_todo_by_id():
    todo_id = VALID_ID
    response = requests.head(f"{BASE_URL}{TODOS_ENDPOINT}/{todo_id}")
    assert response.status_code == 200

def test_head_nonexistent_todo_by_id():
    todo_id = INVALID_ID
    response = requests.head(f"{BASE_URL}{TODOS_ENDPOINT}/{todo_id}")
    assert response.status_code == 404

def test_put_todo_by_id():
    todo_id = VALID_ID
    body = {
        "title": "Wash Dog",
        "doneStatus": False,
        "description": "giving him a bath",
    }
    response = requests.put(f"{BASE_URL}{TODOS_ENDPOINT}/{todo_id}", json=body)
    expected = {
        "id": "1",
        "title": "Wash Dog",
        "doneStatus": "false",
        "description": "giving him a bath",
    }
    assert response.status_code == 200
    assert response.json() == expected

def test_put_nonexistent_todo_by_id():
    todo_id = INVALID_ID
    body = {
        "title": "Wash Dog",
        "doneStatus": False,
        "description": "giving him a bath",
    }
    response = requests.put(f"{BASE_URL}{TODOS_ENDPOINT}/{todo_id}", json=body)
    expected = {
        "errorMessages": [f"Invalid GUID for {todo_id} entity todo"],
    }
    assert response.status_code == 404
    assert response.json() == expected

def test_delete_todo_by_id():
    todo_id = VALID_ID
    response = requests.delete(f"{BASE_URL}{TODOS_ENDPOINT}/{todo_id}")
    assert response.status_code == 200

    # Verify deletion
    proj_relationships_of_todo = requests.get(f"{BASE_URL}{TODOS_ENDPOINT}/{todo_id}")
    expected = {
        "errorMessages": [f"Could not find an instance with todos/{todo_id}"],
    }
    assert proj_relationships_of_todo.status_code == 404
    assert proj_relationships_of_todo.json() == expected

def test_delete_nonexistent_todo_by_id():
    todo_id = INVALID_ID
    response = requests.delete(f"{BASE_URL}{TODOS_ENDPOINT}/{todo_id}")
    expected = {
        "errorMessages": [f"Could not find any instances with todos/{todo_id}"],
    }
    assert response.status_code == 404
    assert response.json() == expected

def test_delete_todo_already_deleted():
    todo_id = VALID_ID
    response = requests.delete(f"{BASE_URL}{TODOS_ENDPOINT}/{todo_id}")
    assert response.status_code == 200

    # Verify deletion
    second_attempt_response = requests.delete(f"{BASE_URL}{TODOS_ENDPOINT}/{todo_id}")
    expected = {
        "errorMessages": [f"Could not find any instances with todos/{todo_id}"],
    }
    assert second_attempt_response.status_code == 404
    assert second_attempt_response.json() == expected