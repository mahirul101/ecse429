import requests
import pytest
import time
import subprocess

BASE_URL = "http://localhost:4567"
TODOS_ENDPOINT = "/todos"
CATEGORIES_ENDPOINT = "/categories"
CATEGORIES_RELATIONSHIP = "categories"
VALID_ID = 1
INVALID_ID = 40
JAR_PATH = "C:/Users/dmytr/Desktop/SCHOOL/Winter_2025/ECSE_429/repo/runTodoManagerRestAPI-1.5.5.jar"

@pytest.fixture(scope="function", autouse=True)
def setup_and_teardown():
    # Start the Java application
    process = subprocess.Popen(["java", "-jar", JAR_PATH])
    
    # Wait for the server to be ready
    server_ready = False
    while not server_ready:
        try:
            requests.get(f"{BASE_URL}{TODOS_ENDPOINT}")
            server_ready = True
        except requests.exceptions.ConnectionError:
            time.sleep(1)

    yield

    # Shutdown the Java application
    requests.get(f"{BASE_URL}/shutdown")
    process.terminate()

def test_head_categories_for_todo():
    todo_id = VALID_ID
    response = requests.head(f"{BASE_URL}{TODOS_ENDPOINT}/{todo_id}/{CATEGORIES_RELATIONSHIP}")
    assert response.status_code == 200

def test_head_categories_for_nonexistent_todo():
    todo_id = INVALID_ID
    response = requests.head(f"{BASE_URL}{TODOS_ENDPOINT}/{todo_id}/{CATEGORIES_RELATIONSHIP}")
    assert response.status_code == 200

def test_get_categories_for_todo():
    todo_id = VALID_ID
    response = requests.get(f"{BASE_URL}{TODOS_ENDPOINT}/{todo_id}/{CATEGORIES_RELATIONSHIP}")
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

def test_get_categories_for_nonexistent_todo():
    todo_id = INVALID_ID
    response = requests.get(f"{BASE_URL}{TODOS_ENDPOINT}/{todo_id}/{CATEGORIES_RELATIONSHIP}")
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

def test_create_relationship_between_todo_and_category():
    todo_id = 2
    body = {"id": "2"}
    response = requests.post(f"{BASE_URL}{TODOS_ENDPOINT}/{todo_id}/{CATEGORIES_RELATIONSHIP}", json=body)
    assert response.status_code == 201

    # Verify the relationship
    created_relationship = requests.get(f"{BASE_URL}{TODOS_ENDPOINT}/{todo_id}/{CATEGORIES_RELATIONSHIP}")
    expected = {
        "categories": [
            {
                "id": "2",
                "title": "Home",
                "description": "",
            },
        ]
    }
    assert created_relationship.status_code == 200
    assert created_relationship.json() == expected

def test_create_relationship_with_nonexistent_todo():
    todo_id = INVALID_ID
    body = {"id": "2"}
    expected = {
        "errorMessages": [f"Could not find parent thing for relationship todos/{todo_id}/categories"],
    }
    response = requests.post(f"{BASE_URL}{TODOS_ENDPOINT}/{todo_id}/{CATEGORIES_RELATIONSHIP}", json=body)
    assert response.status_code == 404
    assert response.json() == expected

def test_delete_relationship_between_todo_and_category():
    todo_id = VALID_ID
    categ_id = 1
    response = requests.delete(f"{BASE_URL}{TODOS_ENDPOINT}/{todo_id}/{CATEGORIES_RELATIONSHIP}/{categ_id}")
    assert response.status_code == 200

    # Verify the deletion
    categ_relationships_of_todo = requests.get(f"{BASE_URL}{TODOS_ENDPOINT}/{todo_id}/{CATEGORIES_RELATIONSHIP}")
    expected = {"categories": []}
    assert categ_relationships_of_todo.status_code == 200
    assert categ_relationships_of_todo.json() == expected

def test_delete_nonexistent_relationship_between_todo_and_category():
    todo_id = VALID_ID
    categ_id = 1
    response = requests.delete(f"{BASE_URL}{TODOS_ENDPOINT}/{todo_id}/{CATEGORIES_RELATIONSHIP}/{categ_id}")
    assert response.status_code == 200

    second_attempt_response = requests.delete(f"{BASE_URL}{TODOS_ENDPOINT}/{todo_id}/{CATEGORIES_RELATIONSHIP}/{categ_id}")
    expected = {
        "errorMessages": [f"Could not find any instances with todos/{todo_id}/categories/{categ_id}"],
    }
    assert second_attempt_response.status_code == 404
    assert second_attempt_response.json() == expected

def test_bidirectional_relationship_creation():
    todo_id = 2
    body = {"id": "2"}
    response = requests.post(f"{BASE_URL}{TODOS_ENDPOINT}/{todo_id}/{CATEGORIES_RELATIONSHIP}", json=body)
    assert response.status_code == 201

    # Verify the todo-category side of the relationship
    created_relationship = requests.get(f"{BASE_URL}{TODOS_ENDPOINT}/{todo_id}/{CATEGORIES_RELATIONSHIP}")
    expected = {
        "categories": [
            {
                "id": "2",
                "title": "Home",
                "description": "",
            },
        ]
    }
    assert created_relationship.status_code == 200
    assert created_relationship.json() == expected

    # Verify the category-todo side of the relationship
    categ_todo_relationships = requests.get(f"{BASE_URL}{CATEGORIES_ENDPOINT}/{body['id']}/{TODOS_ENDPOINT}")
    expected_categ_todo_relationships = {"todos": []}
    assert categ_todo_relationships.status_code == 200
    assert categ_todo_relationships.json() == expected_categ_todo_relationships