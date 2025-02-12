import requests
import pytest
import time
import subprocess

BASE_URL = "http://localhost:4567"
PROJECTS_ENDPOINT = "/projects"
CATEGORIES_ENDPOINT = "/categories"
CATEGORIES_RELATIONSHIP = "categories"
VALID_ID = 1
INVALID_ID = 20
JAR_PATH = "C:/Users/dmytr/Desktop/SCHOOL/Winter_2025/ECSE_429/repo/runTodoManagerRestAPI-1.5.5.jar"

@pytest.fixture(scope="function", autouse=True)
def setup_and_teardown():
    # Start the Java application
    process = subprocess.Popen(["java", "-jar", JAR_PATH])
    
    # Wait for the server to be ready
    server_ready = False
    while not server_ready:
        try:
            requests.get(f"{BASE_URL}{PROJECTS_ENDPOINT}")
            server_ready = True
        except requests.exceptions.ConnectionError:
            time.sleep(1)

    yield

    # Shutdown the Java application
    requests.get(f"{BASE_URL}/shutdown")
    process.terminate()

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
    assert response.json() == expected

def test_get_categories_for_nonexistent_project():
    response = requests.get(f"{BASE_URL}{PROJECTS_ENDPOINT}/{INVALID_ID}/{CATEGORIES_RELATIONSHIP}")
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

def test_head_categories_for_project():
    response = requests.head(f"{BASE_URL}{PROJECTS_ENDPOINT}/{VALID_ID}/{CATEGORIES_RELATIONSHIP}")
    assert response.status_code == 200

def test_head_categories_for_nonexistent_project():
    response = requests.head(f"{BASE_URL}{PROJECTS_ENDPOINT}/{INVALID_ID}/{CATEGORIES_RELATIONSHIP}")
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
    assert relationship.json() == expected

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
    assert response.status_code == 404
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
    assert relationship.json() == expected

    # Check if category to projects relationship is created (bidirectionality) (BUG - NON-EXISTENT)
    categ_project_rel = requests.get(f"{BASE_URL}{CATEGORIES_ENDPOINT}/{body['id']}/{PROJECTS_ENDPOINT}")
    expected_rel = {"projects": []}
    assert categ_project_rel.status_code == 200
    assert categ_project_rel.json() == expected_rel