import requests
import pytest
import time
import subprocess
import psutil

BASE_URL = "http://localhost:4567"
CATEGORIES_ENDPOINT = "/categories"
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


def test_get_all_categories():
    response = requests.get(f"{BASE_URL}{CATEGORIES_ENDPOINT}")
    expected_categories = [
        {
            "id": "1",
            "title": "Office",
            "description": "",
        },
        {
            "id": "2",
            "title": "Home",
            "description": "",
        }
    ]
    assert response.status_code == 200
    response_categories = response.json().get("categories", [])
    # Sort both lists by ID before comparing
    response_categories.sort(key=lambda x: x["id"])
    expected_categories.sort(key=lambda x: x["id"])
    assert response_categories == expected_categories

def test_create_category_without_id_with_title():
    body = {
        "title": "University",
        "description": "",
    }
    response = requests.post(f"{BASE_URL}{CATEGORIES_ENDPOINT}", json=body)
    expected = {
        "id": "3",
        "title": "University",
        "description": "",
    }
    assert response.status_code == 201
    assert response.json() == expected

def test_create_category_without_id_without_title():
    body = {
        "title": "",
        "description": "Studying",
    }
    response = requests.post(f"{BASE_URL}{CATEGORIES_ENDPOINT}", json=body)
    expected = {
        "errorMessages": ["Failed Validation: title : can not be empty"],
    }
    assert response.status_code == 400
    assert response.json() == expected

def test_head_categories():
    response = requests.head(f"{BASE_URL}{CATEGORIES_ENDPOINT}")
    assert response.status_code == 200

def test_create_category():
    response = requests.post(
        f"{BASE_URL}/categories",
        json={"title": "Test Category"}
    )
    assert response.status_code == 201
    assert "id" in response.json()

def test_get_nonexistent_category():
    response = requests.get(f"{BASE_URL}/categories/9999")
    assert response.status_code == 404

def test_malformed_json():
    response = requests.post(
        f"{BASE_URL}/categories",
        data="invalid_json",
        headers={"Content-Type": "application/json"}
    )
    assert response.status_code == 400