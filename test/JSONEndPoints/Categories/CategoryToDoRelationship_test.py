import requests
import pytest
import time
import subprocess
import psutil

BASE_URL = "http://localhost:4567"
CATEGORIES_ENDPOINT = "/categories"
TODOS_ENDPOINT = "/todos"
CATEG_TODOS_RELATIONSHIP = "todos"
CATEGORIES_RELATIONSHIP = "categories"
VALID_ID = 1
INVALID_ID = 20
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
    parent = psutil.Process(process.pid)
    for child in parent.children(recursive=True):  # Kill child processes
        child.terminate()
    process.terminate()
    process.wait()

@pytest.fixture(scope="function", autouse=True)
def create_relationship():
    try:
        requests.post(f"{BASE_URL}{CATEGORIES_ENDPOINT}/{VALID_ID}/{CATEG_TODOS_RELATIONSHIP}", json={"id": "2"})
    except requests.exceptions.RequestException:
        pass

def test_get_all_todos_for_category():
    response = requests.get(f"{BASE_URL}{CATEGORIES_ENDPOINT}/{VALID_ID}/{CATEG_TODOS_RELATIONSHIP}")
    expected = {
        "todos": [
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

def test_get_todos_for_nonexistent_category():
    response = requests.get(f"{BASE_URL}{CATEGORIES_ENDPOINT}/{INVALID_ID}/{CATEG_TODOS_RELATIONSHIP}")
    expected = {
        "todos": [
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

def test_head_todos_for_category():
    response = requests.head(f"{BASE_URL}{CATEGORIES_ENDPOINT}/{VALID_ID}/{CATEG_TODOS_RELATIONSHIP}")
    assert response.status_code == 200

def test_head_todos_for_nonexistent_category():
    response = requests.head(f"{BASE_URL}{CATEGORIES_ENDPOINT}/{INVALID_ID}/{CATEG_TODOS_RELATIONSHIP}")
    assert response.status_code == 200

def test_create_relationship_between_category_and_todo():
    body = {"id": "1"}
    response = requests.post(f"{BASE_URL}{CATEGORIES_ENDPOINT}/{VALID_ID}/{CATEG_TODOS_RELATIONSHIP}", json=body)
    assert response.status_code == 201

    # Verifying that the relationship persists
    relationship = requests.get(f"{BASE_URL}{CATEGORIES_ENDPOINT}/{VALID_ID}/{CATEG_TODOS_RELATIONSHIP}")
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

def test_create_relationship_with_nonexistent_category():
    body = {"id": "1"}
    expected = {
        "errorMessages": [f"Could not find parent thing for relationship categories/{INVALID_ID}/todos"],
    }
    response = requests.post(f"{BASE_URL}{CATEGORIES_ENDPOINT}/{INVALID_ID}/{CATEG_TODOS_RELATIONSHIP}", json=body)
    assert response.status_code == 404
    assert response.json() == expected

def test_delete_relationship_between_category_and_todo():
    todo_id = 1
    response = requests.delete(f"{BASE_URL}{CATEGORIES_ENDPOINT}/{VALID_ID}/{CATEG_TODOS_RELATIONSHIP}/{todo_id}")
    assert response.status_code == 200

    # Verify deletion through get request
    relationship = requests.get(f"{BASE_URL}{CATEGORIES_ENDPOINT}/{VALID_ID}/{CATEG_TODOS_RELATIONSHIP}")
    expected = {"todos": [{
             'description': '',
             'doneStatus': 'false',
             'id': '2',
             'tasksof': [
                 {
                     'id': '1',
                 },
             ],
             'title': 'file paperwork',
         },]}
    assert relationship.status_code == 200
    assert relationship.json() == expected

def test_delete_relationship_with_nonexistent_todo():
    todo_id = 20
    response = requests.delete(f"{BASE_URL}{CATEGORIES_ENDPOINT}/{VALID_ID}/{CATEG_TODOS_RELATIONSHIP}/{todo_id}")
    expected = {
        "errorMessages": [f"Could not find any instances with categories/{VALID_ID}/todos/{todo_id}"],
    }
    assert response.status_code == 404
    assert response.json() == expected

def test_bidirectional_relationship_creation():
    body = {"id": "1"}
    response = requests.post(f"{BASE_URL}{CATEGORIES_ENDPOINT}/{VALID_ID}/{CATEG_TODOS_RELATIONSHIP}", json=body)
    assert response.status_code == 201

    # Check that the relationship exists from category to todos
    relationship = requests.get(f"{BASE_URL}{CATEGORIES_ENDPOINT}/{VALID_ID}/{CATEG_TODOS_RELATIONSHIP}")
    expected = {
        "todos": [
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
    assert relationship.status_code == 200
    assert relationship.json() == expected

    # Check if todo to category relationship is created (SUCCESS - EXISTS)
    todo_category_rel = requests.get(f"{BASE_URL}{TODOS_ENDPOINT}/{body['id']}/{CATEGORIES_RELATIONSHIP}")
    expected_rel = {
        "categories": [
            {
                "id": "1",
                "title": "Office",
                "description": "",
                "todos": [
                    {"id": "2"},
                    {"id": "1"},
                ],
            },
        ]
    }
    assert todo_category_rel.status_code == 200
    assert todo_category_rel.json() == expected_rel

def test_delete_bidirectional_relationship():
    todo_id = 2
    response = requests.delete(f"{BASE_URL}{CATEGORIES_ENDPOINT}/{VALID_ID}/{CATEG_TODOS_RELATIONSHIP}/{todo_id}")
    assert response.status_code == 200

    # Verify deletion through get request
    relationship = requests.get(f"{BASE_URL}{CATEGORIES_ENDPOINT}/{VALID_ID}/{CATEG_TODOS_RELATIONSHIP}")
    expected = {"todos": []}
    assert relationship.status_code == 200
    assert relationship.json() == expected

    # Check if todo to category relationship is deleted (SUCCESS - DELETES)
    todo_category_rel = requests.get(f"{BASE_URL}{TODOS_ENDPOINT}/{todo_id}/{CATEGORIES_RELATIONSHIP}")
    expected_proj = {"categories": []}
    assert todo_category_rel.status_code == 200
    assert todo_category_rel.json() == expected_proj