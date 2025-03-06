import requests
import pytest
import time
import subprocess
import psutil

BASE_URL = "http://localhost:4567"
PROJECTS_ENDPOINT = "/projects"
CATEGORIES_RELATIONSHIP = "categories"
VALID_ID = 1
INVALID_ID = 20
JAR_PATH = "../../runTodoManagerRestAPI-1.5.5.jar"

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
            create_relationship()
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

def create_relationship():
    try:
        requests.post(f"{BASE_URL}{PROJECTS_ENDPOINT}/{VALID_ID}/{CATEGORIES_RELATIONSHIP}", json={"id": "1"})
    except requests.exceptions.RequestException:
        pass

def test_head_categories_for_project():
    response = requests.head(f"{BASE_URL}{PROJECTS_ENDPOINT}/{VALID_ID}/{CATEGORIES_RELATIONSHIP}", headers={"Content-Type": "application/xml"})
    assert response.status_code == 200

def test_head_categories_for_nonexistent_project():
    response = requests.head(f"{BASE_URL}{PROJECTS_ENDPOINT}/{INVALID_ID}/{CATEGORIES_RELATIONSHIP}", headers={"Content-Type": "application/xml"})
    assert response.status_code == 200

def test_post_project_category_relationship():
    body = "<id>2</id>"
    headers = {"Content-Type": "application/xml"}
    response = requests.post(f"{BASE_URL}{PROJECTS_ENDPOINT}/{VALID_ID}/{CATEGORIES_RELATIONSHIP}", data=body, headers=headers)
    expected = '{"errorMessages":["java.lang.IllegalStateException: Expected BEGIN_OBJECT but was STRING at line 1 column 1 path $"]}'
    assert response.status_code == 400
    assert response.text == expected

def test_post_project_category_relationship_with_nonexistent_project():
    body = "<id>2</id>"
    headers = {"Content-Type": "application/xml"}
    response = requests.post(f"{BASE_URL}{PROJECTS_ENDPOINT}/{INVALID_ID}/{CATEGORIES_RELATIONSHIP}", data=body, headers=headers)
    expected = '{"errorMessages":["java.lang.IllegalStateException: Expected BEGIN_OBJECT but was STRING at line 1 column 1 path $"]}'
    assert response.status_code == 400
    assert response.text == expected

def test_delete_project_category_relationship():
    categ_id = 1
    response = requests.delete(f"{BASE_URL}{PROJECTS_ENDPOINT}/{VALID_ID}/{CATEGORIES_RELATIONSHIP}/{categ_id}", headers={"Content-Type": "application/xml"})
    assert response.status_code == 200

    # Verify deletion through get request
    relationship = requests.get(f"{BASE_URL}{PROJECTS_ENDPOINT}/{VALID_ID}/{CATEGORIES_RELATIONSHIP}")
    expected = {"categories": []}
    assert relationship.status_code == 200
    assert relationship.json() == expected

def test_delete_nonexistent_project_category_relationship():
    categ_id = 2
    response = requests.delete(f"{BASE_URL}{PROJECTS_ENDPOINT}/{VALID_ID}/{CATEGORIES_RELATIONSHIP}/{categ_id}", headers={"Content-Type": "application/xml"})
    expected = {
        "errorMessages": [f"Could not find any instances with projects/{VALID_ID}/categories/{categ_id}"],
    }
    assert response.status_code == 404
    assert response.json() == expected