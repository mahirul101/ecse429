import requests
import pytest
import time
import subprocess
import psutil

BASE_URL = "http://localhost:4567"
CATEGORIES_ENDPOINT = "/categories"
CATEG_TODOS_RELATIONSHIP = "todos"
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
def create_relationship():
    try:
        requests.post(f"{BASE_URL}{CATEGORIES_ENDPOINT}/{VALID_ID}/{CATEG_TODOS_RELATIONSHIP}", json={"id": "2"})
    except requests.exceptions.RequestException:
        pass

def test_head_todos_for_category():
    response = requests.head(f"{BASE_URL}{CATEGORIES_ENDPOINT}/{VALID_ID}/{CATEG_TODOS_RELATIONSHIP}", headers={"Content-Type": "application/xml"})
    assert response.status_code == 200

def test_head_todos_for_nonexistent_category():
    response = requests.head(f"{BASE_URL}{CATEGORIES_ENDPOINT}/{INVALID_ID}/{CATEG_TODOS_RELATIONSHIP}", headers={"Content-Type": "application/xml"})
    assert response.status_code == 200

def test_post_category_todo_relationship():
    body = "<id>1</id>"
    headers = {"Content-Type": "application/xml"}
    response = requests.post(f"{BASE_URL}{CATEGORIES_ENDPOINT}/{VALID_ID}/{CATEG_TODOS_RELATIONSHIP}", data=body, headers=headers)
    expected = '{"errorMessages":["java.lang.IllegalStateException: Expected BEGIN_OBJECT but was STRING at line 1 column 1 path $"]}'
    assert response.status_code == 400
    assert response.text == expected

def test_post_category_todo_relationship_with_nonexistent_category():
    body = "<id>1</id>"
    headers = {"Content-Type": "application/xml"}
    response = requests.post(f"{BASE_URL}{CATEGORIES_ENDPOINT}/{INVALID_ID}/{CATEG_TODOS_RELATIONSHIP}", data=body, headers=headers)
    expected = '{"errorMessages":["java.lang.IllegalStateException: Expected BEGIN_OBJECT but was STRING at line 1 column 1 path $"]}'
    assert response.status_code == 400
    assert response.text == expected

def test_delete_category_todo_relationship():
    todo_id = 2
    response = requests.delete(f"{BASE_URL}{CATEGORIES_ENDPOINT}/{VALID_ID}/{CATEG_TODOS_RELATIONSHIP}/{todo_id}", headers={"Content-Type": "application/xml"})
    assert response.status_code == 200

    # Verify deletion through get request
    relationship = requests.get(f"{BASE_URL}{CATEGORIES_ENDPOINT}/{VALID_ID}/{CATEG_TODOS_RELATIONSHIP}", headers={"Content-Type": "application/xml"})
    expected = {"todos": []}
    assert relationship.status_code == 200
    assert relationship.json() == expected

def test_delete_nonexistent_category_todo_relationship():
    todo_id = 20
    response = requests.delete(f"{BASE_URL}{CATEGORIES_ENDPOINT}/{VALID_ID}/{CATEG_TODOS_RELATIONSHIP}/{todo_id}", headers={"Content-Type": "application/xml"})
    expected = {
        "errorMessages": [f"Could not find any instances with categories/{VALID_ID}/todos/{todo_id}"],
    }
    assert response.status_code == 404
    assert response.json() == expected