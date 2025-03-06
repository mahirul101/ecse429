import requests
import pytest
import time
import subprocess
import psutil

BASE_URL = "http://localhost:4567"
PROJECTS_ENDPOINT = "/projects"
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

def test_head_project_by_id():
    response = requests.head(f"{BASE_URL}{PROJECTS_ENDPOINT}/{VALID_ID}", headers={"Content-Type": "application/xml"})
    assert response.status_code == 200

def test_head_nonexistent_project_by_id():
    response = requests.head(f"{BASE_URL}{PROJECTS_ENDPOINT}/{INVALID_ID}", headers={"Content-Type": "application/xml"})
    assert response.status_code == 404

def test_post_project_by_id():
    body = """
    <project>
        <active>true</active>
        <description>Meeting in progress</description>
        <completed>false</completed>
    </project>
    """
    headers = {"Content-Type": "application/xml"}
    response = requests.post(f"{BASE_URL}{PROJECTS_ENDPOINT}/{VALID_ID}", data=body, headers=headers)
    expected = {
        "id": "1",
        "title": "Office Work",
        "completed": "false",
        "active": "true",
        "description": "Meeting in progress",
        "tasks": [
            {"id": "1"},
            {"id": "2"},
        ],
    }
    assert response.status_code == 200

    # Sort the tasks list in both actual and expected responses
    actual_response = response.json()
    actual_response["tasks"] = sorted(actual_response["tasks"], key=lambda x: x["id"])
    expected["tasks"] = sorted(expected["tasks"], key=lambda x: x["id"])

    assert actual_response == expected

def test_post_nonexistent_project_by_id():
    body = """
    <project>
        <active>true</active>
        <description>Meeting in progress</description>
        <completed>false</completed>
    </project>
    """
    headers = {"Content-Type": "application/xml"}
    response = requests.post(f"{BASE_URL}{PROJECTS_ENDPOINT}/{INVALID_ID}", data=body, headers=headers)
    expected = {
        "errorMessages": [f"No such project entity instance with GUID or ID {INVALID_ID} found"],
    }
    assert response.status_code == 404
    assert response.json() == expected

def test_put_project_by_id():
    body = """
    <project>
        <title>University Work</title>
        <active>true</active>
        <description>Meeting in progress</description>
    </project>
    """
    headers = {"Content-Type": "application/xml"}
    response = requests.put(f"{BASE_URL}{PROJECTS_ENDPOINT}/{VALID_ID}", data=body, headers=headers)
    expected = {
        "id": "1",
        "title": "University Work",
        "active": "true",
        "completed": "false",
        "description": "Meeting in progress",
    }
    assert response.status_code == 200
    assert response.json() == expected

def test_put_nonexistent_project_by_id():
    body = """
    <project>
        <title>University Work</title>
        <active>true</active>
        <description>Meeting in progress</description>
    </project>
    """
    headers = {"Content-Type": "application/xml"}
    response = requests.put(f"{BASE_URL}{PROJECTS_ENDPOINT}/{INVALID_ID}", data=body, headers=headers)
    expected = {
        "errorMessages": [f"Invalid GUID for {INVALID_ID} entity project"],
    }
    assert response.status_code == 404
    assert response.json() == expected

def test_delete_project_by_id():
    response = requests.delete(f"{BASE_URL}{PROJECTS_ENDPOINT}/{VALID_ID}", headers={"Content-Type": "application/xml"})
    assert response.status_code == 200

def test_delete_nonexistent_project_by_id():
    response = requests.delete(f"{BASE_URL}{PROJECTS_ENDPOINT}/{INVALID_ID}", headers={"Content-Type": "application/xml"})
    expected = {
        "errorMessages": [f"Could not find any instances with projects/{INVALID_ID}"],
    }
    assert response.status_code == 404
    assert response.json() == expected