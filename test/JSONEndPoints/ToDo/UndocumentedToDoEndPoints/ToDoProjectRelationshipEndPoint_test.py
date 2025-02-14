import requests
import pytest
import time
import subprocess
import psutil

BASE_URL = "http://localhost:4567"
TODOS_ENDPOINT = "/todos"
TODO_PROJ_RELATIONSHIP = "tasksof"
JAR_PATH = "../../../../runTodoManagerRestAPI-1.5.5.jar"

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

def test_get_projects_for_todos():
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

    response = requests.get(f"{BASE_URL}{TODOS_ENDPOINT}/{TODO_PROJ_RELATIONSHIP}")
    assert response.status_code == 200

    # Sort the tasks list within each project before comparing
    response_projects = response.json().get("projects", [])
    for project in response_projects:
        project["tasks"].sort(key=lambda x: x["id"])
    for project in expected["projects"]:
        project["tasks"].sort(key=lambda x: x["id"])

    assert response_projects == expected["projects"]