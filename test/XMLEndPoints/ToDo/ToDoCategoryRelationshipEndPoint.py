import requests
import pytest
import time
import subprocess
import psutil

BASE_URL = "http://localhost:4567"
TODOS_ENDPOINT = "/todos"
CATEG_RELATIONSHIP = "categories"
VALID_ID = 2
INVALID_ID = 40
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

def test_post_todo_category_relationship():
    todo_id = VALID_ID
    body = "<id>2</id>"
    headers = {"Content-Type": "application/xml"}
    response = requests.post(f"{BASE_URL}{TODOS_ENDPOINT}/{todo_id}/{CATEG_RELATIONSHIP}", data=body, headers=headers)
    expected = '{"errorMessages":["java.lang.IllegalStateException: Expected BEGIN_OBJECT but was STRING at line 1 column 1 path $"]}'
    assert response.status_code == 400
    assert response.text == expected

def test_post_todo_category_relationship_with_nonexistent_todo():
    todo_id = INVALID_ID
    body = "<id>2</id>"
    headers = {"Content-Type": "application/xml"}
    expected = '{"errorMessages":["java.lang.IllegalStateException: Expected BEGIN_OBJECT but was STRING at line 1 column 1 path $"]}'
    response = requests.post(f"{BASE_URL}{TODOS_ENDPOINT}/{todo_id}/{CATEG_RELATIONSHIP}", data=body, headers=headers)
    assert response.status_code == 400
    assert response.text == expected

def test_delete_todo_category_relationship():
    todo_id = 1
    categ_id = 1
    headers = {"Content-Type": "application/xml"}
    response = requests.delete(f"{BASE_URL}{TODOS_ENDPOINT}/{todo_id}/{CATEG_RELATIONSHIP}/{categ_id}", headers=headers)
    assert response.status_code == 200

    # Verify deletion
    categ_relationships_of_todo = requests.get(f"{BASE_URL}{TODOS_ENDPOINT}/{todo_id}/{CATEG_RELATIONSHIP}", headers=headers)
    expected = {"categories": []}
    assert categ_relationships_of_todo.status_code == 200
    assert categ_relationships_of_todo.json() == expected

def test_delete_nonexistent_todo_category_relationship():
    todo_id = 1
    categ_id = 1
    headers = {"Content-Type": "application/xml"}
    response = requests.delete(f"{BASE_URL}{TODOS_ENDPOINT}/{todo_id}/{CATEG_RELATIONSHIP}/{categ_id}", headers=headers)
    assert response.status_code == 200

    # Verify deletion
    second_attempt_response = requests.delete(f"{BASE_URL}{TODOS_ENDPOINT}/{todo_id}/{CATEG_RELATIONSHIP}/{categ_id}", headers=headers)
    expected = {
        "errorMessages": [f"Could not find any instances with todos/{todo_id}/categories/{categ_id}"],
    }
    assert second_attempt_response.status_code == 404
    assert second_attempt_response.json() == expected