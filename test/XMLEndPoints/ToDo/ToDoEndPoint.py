import requests
import pytest
import time
import subprocess
import psutil

BASE_URL = "http://localhost:4567"
TODOS_ENDPOINT = "/todos"
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

def test_create_todo_without_id():
    body = """
    <todo>
        <title>Clean Cupboard</title>
        <doneStatus>false</doneStatus>
        <description>Home Chore to be done</description>
    </todo>
    """
    headers = {"Content-Type": "application/xml"}
    response = requests.post(f"{BASE_URL}{TODOS_ENDPOINT}", data=body, headers=headers)
    expected = {
        "id": "3",
        "title": "Clean Cupboard",
        "doneStatus": "false",
        "description": "Home Chore to be done",
    }
    assert response.status_code == 201
    assert response.json() == expected

def test_create_todo_without_id_missing_title():
    body = """
    <todo>
        <doneStatus>false</doneStatus>
        <description>Give him food</description>
    </todo>
    """
    headers = {"Content-Type": "application/xml"}
    expected = {
        "errorMessages": ["title : field is mandatory"],
    }
    response = requests.post(f"{BASE_URL}{TODOS_ENDPOINT}", data=body, headers=headers)
    assert response.status_code == 400
    assert response.json() == expected

def test_create_todo_with_extra_attribute():
    body = """
    <todo>
        <title>Clean Cupboard</title>
        <doneStatus>false</doneStatus>
        <description>Home Chore to be done</description>
        <monthCreated>OCT</monthCreated>
    </todo>
    """
    headers = {"Content-Type": "application/xml"}
    expected = {
        "errorMessages": ["Could not find field: monthCreated"],
    }
    response = requests.post(f"{BASE_URL}{TODOS_ENDPOINT}", data=body, headers=headers)
    assert response.status_code == 400
    assert response.json() == expected

def test_head_todos():
    headers = {"Content-Type": "application/xml"}
    response = requests.head(f"{BASE_URL}{TODOS_ENDPOINT}", headers=headers)
    assert response.status_code == 200