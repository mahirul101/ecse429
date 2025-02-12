import requests
import pytest
import time
import subprocess

BASE_URL = "http://localhost:4567"
CATEGORIES_ENDPOINT = "/categories"
JAR_PATH = r"C:/Users/dmytr/Desktop/SCHOOL/Winter_2025/ECSE_429/repo/runTodoManagerRestAPI-1.5.5.jar"

'''
@pytest.fixture(scope="function", autouse=True)
def setup_and_teardown():
    # Start the Java application
    process = subprocess.Popen(
    ["java", "-jar", JAR_PATH],
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE
    )
    stdout, stderr = process.communicate()
    print(stdout.decode())
    print(stderr.decode())

    
    print(f"Server ready: {process}")
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
'''
def test_get_all_categories():
    response = requests.get(f"{BASE_URL}{CATEGORIES_ENDPOINT}")
    expected = {
        "categories": [
            {
                "id": "2",
                "title": "Home",
                "description": "",
            },
            {
                "id": "1",
                "title": "Office",
                "description": "",
            },
        ]
    }
    assert response.status_code == 200
    assert response.json() == expected

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