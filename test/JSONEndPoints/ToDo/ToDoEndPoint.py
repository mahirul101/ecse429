import requests
import pytest
import time
import subprocess

BASE_URL = "http://localhost:4567"
TODOS_ENDPOINT = "/todos"
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

def test_get_all_todos():
    response = requests.get(f"{BASE_URL}{TODOS_ENDPOINT}")
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
    assert response.status_code == 200
    assert response.json() == expected

def test_get_todos_by_done_status():
    response = requests.get(f"{BASE_URL}{TODOS_ENDPOINT}", params={"doneStatus": "false"})
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
    assert response.status_code == 200
    assert response.json() == expected

def test_get_todos_by_done_status_and_title():
    response = requests.get(f"{BASE_URL}{TODOS_ENDPOINT}", params={"doneStatus": "false", "title": "file paperwork"})
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

def test_create_todo_without_id():
    body = {
        "title": "feed dog",
        "doneStatus": False,
        "description": "give him food",
    }
    response = requests.post(f"{BASE_URL}{TODOS_ENDPOINT}", json=body)
    expected = {
        "id": "3",
        "title": "feed dog",
        "doneStatus": "false",
        "description": "give him food",
    }
    assert response.status_code == 201
    assert response.json() == expected

def test_create_todo_without_title():
    body = {
        "doneStatus": False,
        "description": "give him food",
    }
    expected = {
        "errorMessages": ["title : field is mandatory"],
    }
    response = requests.post(f"{BASE_URL}{TODOS_ENDPOINT}", json=body)
    assert response.status_code == 400
    assert response.json() == expected

def test_create_todo_with_extra_attribute():
    body = {
        "title": "Feed my dog",
        "doneStatus": False,
        "description": "give him food",
        "monthCreated": "OCT",
    }
    expected = {
        "errorMessages": ["Could not find field: monthCreated"],
    }
    response = requests.post(f"{BASE_URL}{TODOS_ENDPOINT}", json=body)
    assert response.status_code == 400
    assert response.json() == expected

def test_head_todos():
    response = requests.head(f"{BASE_URL}{TODOS_ENDPOINT}")
    assert response.status_code == 200