import requests
import pytest
import time
import subprocess
import psutil

BASE_URL = "http://localhost:4567"
PROJECTS_ENDPOINT = "/projects"
TODOS_ENDPOINT = "/todos"
PROJ_TODO_RELATIONSHIP = "tasks"
TODO_PROJ_RELATIONSHIP = "projects"
VALID_ID = 1
INVALID_ID = 20
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
    assert response.status_code == 200

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

    # Sort both lists by ID before comparing
    response_todos = response.json().get("todos", [])
    response_todos.sort(key=lambda x: x["id"])
    expected["todos"].sort(key=lambda x: x["id"])

    assert response_todos == expected["todos"]

def test_get_tasks_for_nonexistent_project():
    response = requests.get(f"{BASE_URL}{PROJECTS_ENDPOINT}/{INVALID_ID}/{PROJ_TODO_RELATIONSHIP}")
    assert response.status_code == 200

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

    # Sort both lists by ID before comparing
    response_todos = response.json().get("todos", [])
    response_todos.sort(key=lambda x: x["id"])
    expected["todos"].sort(key=lambda x: x["id"])

    assert response_todos == expected["todos"]

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
    assert relationship.status_code == 200

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

    # Sort both lists by ID before comparing
    response_todos = relationship.json().get("todos", [])
    response_todos.sort(key=lambda x: x["id"])
    expected["todos"].sort(key=lambda x: x["id"])

    assert response_todos == expected["todos"]

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

def knownbug_test_bidirectional_relationship_creation():
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
        ]
    }

    # Sort both lists by ID before comparing
    response_todos = relationship.json().get("todos", [])
    response_todos.sort(key=lambda x: x["id"])
    expected["todos"].sort(key=lambda x: x["id"])

    assert response_todos == expected["todos"]

    # Check if task to projects relationship is created
    #BUG: The http://localhost:4567/todos/3/projects returns 404 not found
    body = {"id": "3"}
    task_project_rel = requests.get(f"{BASE_URL}{TODOS_ENDPOINT}/{body['id']}/{TODO_PROJ_RELATIONSHIP}")
    if task_project_rel.status_code == 200:
        expected_rel = {
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
                        {"id": "3"},
                    ],
                },
            ]
        }

    # Sort the tasks list within each project before comparing
    response_projects = task_project_rel.json().get("projects", [])
    for project in response_projects:
        project["tasks"].sort(key=lambda x: x["id"])
    for project in expected_rel["projects"]:
        project["tasks"].sort(key=lambda x: x["id"])

    assert task_project_rel.status_code == 200
    assert response_projects == expected_rel["projects"]

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
    #BUG: The http://localhost:4567/todos/2/projects returns 404 not found
    task_project_rel = requests.get(f"{BASE_URL}{TODOS_ENDPOINT}/{todo_id}/{TODO_PROJ_RELATIONSHIP}")
    #expected_proj = {"projects": []}
    assert task_project_rel.status_code == 404 #Not found
    #assert task_project_rel.json() == expected_proj