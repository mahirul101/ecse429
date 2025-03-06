from behave import given
import requests

BASE_URL = "http://localhost:4567"

@given('the server is running')
def step_impl(context):
    response = requests.get(f"{BASE_URL}/projects")
    assert response.status_code == 200