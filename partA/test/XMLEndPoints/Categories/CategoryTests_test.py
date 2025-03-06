import requests
import pytest
import time
import subprocess
import psutil

BASE_URL = "http://localhost:4567"
CATEGORIES_ENDPOINT = "/categories"
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

def test_create_category_without_id_with_title():
    body = """
    <category>
        <title>University</title>
        <description></description>
    </category>
    """
    headers = {"Content-Type": "application/xml"}
    response = requests.post(f"{BASE_URL}{CATEGORIES_ENDPOINT}", data=body, headers=headers)
    expected = {
        "id": "3",
        "title": "University",
        "description": "",
    }
    assert response.status_code == 201
    assert response.json() == expected

def test_create_category_without_id_without_title():
    body = """
    <category>
        <title></title>
        <description>Meeting for 429 group</description>
    </category>
    """
    headers = {"Content-Type": "application/xml"}
    response = requests.post(f"{BASE_URL}{CATEGORIES_ENDPOINT}", data=body, headers=headers)
    expected = {
        "errorMessages": ["Failed Validation: title : can not be empty"],
    }
    assert response.status_code == 400
    assert response.json() == expected

def test_head_categories():
    headers = {"Content-Type": "application/xml"}
    response = requests.head(f"{BASE_URL}{CATEGORIES_ENDPOINT}", headers=headers)
    assert response.status_code == 200