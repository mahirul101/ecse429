import requests
import pytest
import time
import subprocess

BASE_URL = "http://localhost:4567"
TODOS_ENDPOINT = "/todos"
CATEGORIES_RELATIONSHIP = "categories"
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

def test_get_categories_for_todos():
    expected = {
        "categories": [
            {
                "id": "1",
                "title": "Office",
                "description": "",
            },
        ]
    }

    response = requests.get(f"{BASE_URL}{TODOS_ENDPOINT}/{CATEGORIES_RELATIONSHIP}")
    assert response.status_code == 200
    assert response.json() == expected