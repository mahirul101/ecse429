import requests
import pytest
import time
import subprocess
import psutil

BASE_URL = "http://localhost:4567"
CATEGORIES_ENDPOINT = "/categories"
PROJECTS_ENDPOINT = "/projects"
CATEG_PROJ_RELATIONSHIP = "projects"
CATEGORIES_RELATIONSHIP = "categories"
VALID_ID = 1
VALID_ID2 = 2
INVALID_ID = 20
JAR_PATH = "../../../runTodoManagerRestAPI-1.5.5.jar"


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
        requests.post(f"{BASE_URL}{CATEGORIES_ENDPOINT}/{VALID_ID}/{CATEG_PROJ_RELATIONSHIP}", json={"id": "1"})
    except requests.exceptions.RequestException:
        pass

def test_get_all_projects_for_category():
    response = requests.get(f"{BASE_URL}{CATEGORIES_ENDPOINT}/{VALID_ID}/{CATEG_PROJ_RELATIONSHIP}")
    assert response.status_code == 200

    expected = {
        "projects": [
            {
                "id": "1",
                "title": "Office Work",
                "completed": "false",
                "active": "false",
                "description": "",
                "tasks": [
                    {"id": "2"},
                    {"id": "1"},
                ],
            },
        ]
    }

    # Sort the tasks list within each project before comparing
    response_projects = response.json().get("projects", [])
    for project in response_projects:
        project["tasks"].sort(key=lambda x: x["id"])
    for project in expected["projects"]:
        project["tasks"].sort(key=lambda x: x["id"])

    assert response_projects == expected["projects"]


def test_get_projects_for_nonexistent_category():
    response = requests.get(f"{BASE_URL}{CATEGORIES_ENDPOINT}/{INVALID_ID}/{CATEG_PROJ_RELATIONSHIP}")
    assert response.status_code == 200

    expected = {
        "projects": [
            {
                "id": "1",
                "title": "Office Work",
                "completed": "false",
                "active": "false",
                "description": "",
                "tasks": [
                    {"id": "2"},
                    {"id": "1"},
                ],
            },
        ]
    }

    # Sort the tasks list within each project before comparing
    response_projects = response.json().get("projects", [])
    for project in response_projects:
        project["tasks"].sort(key=lambda x: x["id"])
    for project in expected["projects"]:
        project["tasks"].sort(key=lambda x: x["id"])

    assert response_projects == expected["projects"]

def test_head_projects_for_category():
    response = requests.head(f"{BASE_URL}{CATEGORIES_ENDPOINT}/{VALID_ID}/{CATEG_PROJ_RELATIONSHIP}")
    assert response.status_code == 200

def test_head_projects_for_nonexistent_category():
    response = requests.head(f"{BASE_URL}{CATEGORIES_ENDPOINT}/{INVALID_ID}/{CATEG_PROJ_RELATIONSHIP}")
    assert response.status_code == 200

def test_create_relationship_between_category_and_project():
    body = {"id": "1"}
    response = requests.post(f"{BASE_URL}{CATEGORIES_ENDPOINT}/{VALID_ID2}/{CATEG_PROJ_RELATIONSHIP}", json=body)
    assert response.status_code == 201

def test_create_relationship_with_nonexistent_category():
    body = {"id": "1"}
    expected = {
        "errorMessages": ["Could not find parent thing for relationship categories/20/projects"],
    }
    response = requests.post(f"{BASE_URL}{CATEGORIES_ENDPOINT}/{INVALID_ID}/{CATEG_PROJ_RELATIONSHIP}", json=body)
    assert response.status_code == 404
    assert response.json() == expected

def test_create_relationship_with_nonexistent_project():
    body = {"id": "20"}
    expected = {
        "errorMessages": ["Could not find thing matching value for id"],
    }
    response = requests.post(f"{BASE_URL}{CATEGORIES_ENDPOINT}/{VALID_ID}/{CATEG_PROJ_RELATIONSHIP}", json=body)
    assert response.status_code == 404
    assert response.json() == expected

def test_delete_relationship_between_category_and_project():
    proj_id = 1
    response = requests.delete(f"{BASE_URL}{CATEGORIES_ENDPOINT}/{VALID_ID}/{CATEG_PROJ_RELATIONSHIP}/{proj_id}")
    assert response.status_code == 200

    # Verify deletion through get request
    relationship = requests.get(f"{BASE_URL}{CATEGORIES_ENDPOINT}/{VALID_ID}/{CATEG_PROJ_RELATIONSHIP}")
    expected = {"projects": []}
    assert relationship.status_code == 200
    assert relationship.json() == expected

def test_delete_relationship_with_nonexistent_project():
    proj_id = 2
    response = requests.delete(f"{BASE_URL}{CATEGORIES_ENDPOINT}/{VALID_ID}/{CATEG_PROJ_RELATIONSHIP}/{proj_id}")
    expected = {
        "errorMessages": [f"Could not find any instances with categories/{VALID_ID}/projects/{proj_id}"],
    }
    assert response.status_code == 404
    assert response.json() == expected

def test_bidirectional_relationship_creation():
    body = {"id": "1"}
    response = requests.post(f"{BASE_URL}{CATEGORIES_ENDPOINT}/{VALID_ID2}/{CATEG_PROJ_RELATIONSHIP}", json=body)
    assert response.status_code == 201

    # Check that the relationship exists from category to projects
    relationship = requests.get(f"{BASE_URL}{CATEGORIES_ENDPOINT}/{VALID_ID2}/{CATEG_PROJ_RELATIONSHIP}")
    assert relationship.status_code == 200

    expected = {
        "projects": [
            {
                "id": "1",
                "title": "Office Work",
                "completed": "false",
                "active": "false",
                "description": "",
                "tasks": [
                    {"id": "2"},
                    {"id": "1"},
                ],
            },
        ]
    }

    # Sort the tasks list within each project before comparing
    response_projects = relationship.json().get("projects", [])
    for project in response_projects:
        project["tasks"].sort(key=lambda x: x["id"])
    for project in expected["projects"]:
        project["tasks"].sort(key=lambda x: x["id"])

    assert response_projects == expected["projects"]

    # Check if project to category relationship is created (FAILURE - NONEXISTENT)
    proj_category_rel = requests.get(f"{BASE_URL}{PROJECTS_ENDPOINT}/{body['id']}/{CATEGORIES_RELATIONSHIP}")
    expected_rel = {"categories": []}
    assert proj_category_rel.status_code == 200
    assert proj_category_rel.json() == expected_rel

def test_delete_bidirectional_relationship():
    proj_id = 1
    response = requests.delete(f"{BASE_URL}{CATEGORIES_ENDPOINT}/{VALID_ID}/{CATEG_PROJ_RELATIONSHIP}/{proj_id}")
    assert response.status_code == 200

    # Verify deletion through get request
    relationship = requests.get(f"{BASE_URL}{CATEGORIES_ENDPOINT}/{VALID_ID}/{CATEG_PROJ_RELATIONSHIP}")
    expected = {"projects": []}
    assert relationship.status_code == 200
    assert relationship.json() == expected

    # Check if project to category relationship is deleted (SUCCESS)
    proj_category_rel = requests.get(f"{BASE_URL}{PROJECTS_ENDPOINT}/{proj_id}/{CATEGORIES_RELATIONSHIP}")
    expected_proj = {"categories": []}
    assert proj_category_rel.status_code == 200
    assert proj_category_rel.json() == expected_proj