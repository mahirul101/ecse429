import requests
import pytest
import time
import subprocess
import psutil

BASE_URL = "http://localhost:4567"
CATEGORIES_ENDPOINT = "/categories"
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

def test_get_category_by_id():
    response = requests.get(f"{BASE_URL}{CATEGORIES_ENDPOINT}/{VALID_ID}")
    expected = {
        "categories": [
            {
                "id": "1",
                "title": "Office",
                "description": "",
            },
        ]
    }
    assert response.status_code == 200
    assert response.json() == expected

def test_get_nonexistent_category_by_id():
    response = requests.get(f"{BASE_URL}{CATEGORIES_ENDPOINT}/{INVALID_ID}")
    expected = {
        "errorMessages": [f"Could not find an instance with categories/{INVALID_ID}"],
    }
    assert response.status_code == 404
    assert response.json() == expected

def test_head_category_by_id():
    response = requests.head(f"{BASE_URL}{CATEGORIES_ENDPOINT}/{VALID_ID}")
    assert response.status_code == 200

def test_head_nonexistent_category_by_id():
    response = requests.head(f"{BASE_URL}{CATEGORIES_ENDPOINT}/{INVALID_ID}")
    assert response.status_code == 404

def test_post_category_by_id():
    body = {"title": "College"}
    response = requests.post(f"{BASE_URL}{CATEGORIES_ENDPOINT}/{VALID_ID}", json=body)
    expected = {
        "id": "1",
        "title": "College",
        "description": "",
    }
    assert response.status_code == 200
    assert response.json() == expected

def test_post_nonexistent_category_by_id():
    body = {"title": "College"}
    response = requests.post(f"{BASE_URL}{CATEGORIES_ENDPOINT}/{INVALID_ID}", json=body)
    expected = {
        "errorMessages": [f"No such category entity instance with GUID or ID {INVALID_ID} found"],
    }
    assert response.status_code == 404
    assert response.json() == expected

def test_put_category_by_id():
    body = {"title": "College"}
    response = requests.put(f"{BASE_URL}{CATEGORIES_ENDPOINT}/{VALID_ID}", json=body)
    expected = {
        "id": "1",
        "title": "College",
        "description": "",
    }
    assert response.status_code == 200
    assert response.json() == expected

def test_put_nonexistent_category_by_id():
    body = {"title": "College"}
    response = requests.put(f"{BASE_URL}{CATEGORIES_ENDPOINT}/{INVALID_ID}", json=body)
    expected = {
        "errorMessages": [f"Invalid GUID for {INVALID_ID} entity category"],
    }
    assert response.status_code == 404
    assert response.json() == expected

def test_delete_category_by_id():
    response = requests.delete(f"{BASE_URL}{CATEGORIES_ENDPOINT}/{VALID_ID}")
    assert response.status_code == 200

def test_delete_nonexistent_category_by_id():
    response = requests.delete(f"{BASE_URL}{CATEGORIES_ENDPOINT}/{INVALID_ID}")
    expected = {
        "errorMessages": [f"Could not find any instances with categories/{INVALID_ID}"],
    }
    assert response.status_code == 404
    assert response.json() == expected