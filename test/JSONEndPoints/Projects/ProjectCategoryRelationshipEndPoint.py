import requests
import pytest
import time
import subprocess
import psutil

BASE_URL = "http://localhost:4567"
PROJECTS_ENDPOINT = "/projects"
CATEGORIES_ENDPOINT = "/categories"
CATEGORIES_RELATIONSHIP = "categories"
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

@pytest.fixture(scope="function", autouse=True)
def create_relationship():
    try:
        requests.post(f"{BASE_URL}{PROJECTS_ENDPOINT}/{VALID_ID}/{CATEGORIES_RELATIONSHIP}", json={"id": "1"})
    except requests.exceptions.RequestException:
        pass

def test_get_all_categories_for_project():
    response = requests.get(f"{BASE_URL}{PROJECTS_ENDPOINT}/{VALID_ID}/{CATEGORIES_RELATIONSHIP}")
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
    response_categories = response.json().get("categories", [])
    response_categories.sort(key=lambda x: x["id"])
    expected["categories"].sort(key=lambda x: x["id"])
    assert response_categories == expected["categories"]

def test_get_categories_for_nonexistent_project():
    response = requests.get(f"{BASE_URL}{PROJECTS_ENDPOINT}/{INVALID_ID}/{CATEGORIES_RELATIONSHIP}")
    expected = {
        "errorMessages": [f"Could not find any instances with projects/{INVALID_ID}/categories"]
    }
    # This is a bug in the API, it should return a 404 status code # 
    assert response.status_code == 200
    assert response.json() == expected

def test_head_categories_for_project():
    response = requests.head(f"{BASE_URL}{PROJECTS_ENDPOINT}/{VALID_ID}/{CATEGORIES_RELATIONSHIP}")
    assert response.status_code == 200

def test_head_categories_for_nonexistent_project():
    response = requests.head(f"{BASE_URL}{PROJECTS_ENDPOINT}/{INVALID_ID}/{CATEGORIES_RELATIONSHIP}")
    # This is a bug in the API, it should return a 404 status code #
    assert response.status_code == 200

def test_create_relationship_between_project_and_category():
    body = {"id": "2"}
    response = requests.post(f"{BASE_URL}{PROJECTS_ENDPOINT}/{VALID_ID}/{CATEGORIES_RELATIONSHIP}", json=body)
    assert response.status_code == 201

    # Verifying that the relationship persists
    relationship = requests.get(f"{BASE_URL}{PROJECTS_ENDPOINT}/{VALID_ID}/{CATEGORIES_RELATIONSHIP}")
    expected = {
        "categories": [
            {
                "id": "1",
                "title": "Office",
                "description": "",
            },
            {
                "id": "2",
                "title": "Home",
                "description": "",
            },
        ]
    }
    assert relationship.status_code == 200
    response_categories = relationship.json().get("categories", [])
    response_categories.sort(key=lambda x: x["id"])
    expected["categories"].sort(key=lambda x: x["id"])
    assert response_categories == expected["categories"]

def test_create_relationship_with_nonexistent_project():
    body = {"id": "1"}
    expected = {
        "errorMessages": [f"Could not find parent thing for relationship projects/{INVALID_ID}/categories"],
    }
    response = requests.post(f"{BASE_URL}{PROJECTS_ENDPOINT}/{INVALID_ID}/{CATEGORIES_RELATIONSHIP}", json=body)
    assert response.status_code == 404
    assert response.json() == expected

def test_delete_relationship_between_project_and_category():
    categ_id = 1
    response = requests.delete(f"{BASE_URL}{PROJECTS_ENDPOINT}/{VALID_ID}/{CATEGORIES_RELATIONSHIP}/{categ_id}")
    assert response.status_code == 200

    # Verify deletion through get request
    relationship = requests.get(f"{BASE_URL}{PROJECTS_ENDPOINT}/{VALID_ID}/{CATEGORIES_RELATIONSHIP}")
    expected = {"categories": []}
    assert relationship.status_code == 200
    assert relationship.json() == expected

def test_delete_nonexistent_relationship_between_project_and_category():
    categ_id = 2
    response = requests.delete(f"{BASE_URL}{PROJECTS_ENDPOINT}/{VALID_ID}/{CATEGORIES_RELATIONSHIP}/{categ_id}")
    expected = {
        "errorMessages": [f"Could not find any instances with projects/{VALID_ID}/categories/{categ_id}"],
    }
    # This is a bug in the API, it should return a 404 status code #
    assert response.status_code == 200
    assert response.json() == expected

def test_bidirectional_relationship_creation():
    body = {"id": "2"}
    response = requests.post(f"{BASE_URL}{PROJECTS_ENDPOINT}/{VALID_ID}/{CATEGORIES_RELATIONSHIP}", json=body)
    assert response.status_code == 201

    # Check that the relationship exists from projects to categories (SUCCESS - EXISTS)
    relationship = requests.get(f"{BASE_URL}{PROJECTS_ENDPOINT}/{VALID_ID}/{CATEGORIES_RELATIONSHIP}")
    expected = {
        "categories": [
            {
                "id": "1",
                "title": "Office",
                "description": "",
            },
            {
                "id": "2",
                "title": "Home",
                "description": "",
            },
        ]
    }
    assert relationship.status_code == 200
    response_categories = relationship.json().get("categories", [])
    response_categories.sort(key=lambda x: x["id"])
    expected["categories"].sort(key=lambda x: x["id"])
    assert response_categories == expected["categories"]

    # Check if category to projects relationship is created (bidirectionality) (BUG - NON-EXISTENT)
    categ_project_rel = requests.get(f"{BASE_URL}{CATEGORIES_ENDPOINT}/{body['id']}/{PROJECTS_ENDPOINT}")
    expected_rel = {"projects": []}
    assert categ_project_rel.status_code == 200
    assert categ_project_rel.json() == expected_rel