import requests
import pytest
import time
import subprocess

BASE_URL = "http://localhost:4567"
CATEGORIES_ENDPOINT = "/categories"
PROJECTS_ENDPOINT = "/projects"
CATEG_PROJ_RELATIONSHIP = "projects"
CATEGORIES_RELATIONSHIP = "categories"
VALID_ID = 1
VALID_ID2 = 2
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
            requests.get(f"{BASE_URL}{CATEGORIES_ENDPOINT}")
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
        requests.post(f"{BASE_URL}{CATEGORIES_ENDPOINT}/{VALID_ID}/{CATEG_PROJ_RELATIONSHIP}", json={"id": "1"})
    except requests.exceptions.RequestException:
        pass

def test_get_all_projects_for_category():
    response = requests.get(f"{BASE_URL}{CATEGORIES_ENDPOINT}/{VALID_ID}/{CATEG_PROJ_RELATIONSHIP}")
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
    assert response.status_code == 200
    assert response.json() == expected


def test_get_projects_for_nonexistent_category():
    response = requests.get(f"{BASE_URL}{CATEGORIES_ENDPOINT}/{INVALID_ID}/{CATEG_PROJ_RELATIONSHIP}")
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
    assert response.status_code == 200
    assert response.json() == expected

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
    expected = {
        "projects": [
            {
                "id": "1",
                "title": "Office Work",
                "completed": "false",
                "active": "false",
                "description": "",
                "tasks": [
                    {"id": "1"},
                    {"id": "2"},
                ],
            },
        ]
    }
    assert relationship.status_code == 200
    assert relationship.json() == expected

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