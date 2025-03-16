
from behave import given, when, then
import requests
import json

BASE_URL = "http://localhost:4567"

@given('the following categories exist:')
def step_categories_exist(context):
    categories = json.loads(context.text)
    for category in categories:
        name = category['name']
        description = category['description']
        category_data = {"title": name, "description": description}
        response = requests.post(f"{BASE_URL}/categories", json=category_data)
        assert response.status_code == 201, f"Failed to create category {name}"

@when('the user retrieves the category with name "{name}" categories')
def step_retrieve_category(context, name):
    response = requests.get(f"{BASE_URL}/categories")
    categories = response.json().get("categories", [])

    category_id = None
    for category in categories:
        if category['title'] == name:
            category_id = category['id']
            break

    if category_id:
        response = requests.get(f"{BASE_URL}/categories/{category_id}")
        context.response = response
        print(f"Response: {context.response.json()}")
    else:
        context.response = response

@then('the response should contain the category details with name "{name}"')
def step_check_category_details(context, name):
    assert context.response.status_code == 200, "Category not found"
    category = context.response.json()
    assert category['categories'][0]['title'] == name, f"Expected category name '{name}', but got '{category['title']}'"

@then('the category description should be "{description}"')
def step_check_category_description(context, description):
    category = context.response.json()
    assert category['categories'][0]['description'] == description, f"Expected category description '{description}', but got '{category['description']}'"


@given('the category with name "{name}" has related items')
def step_category_has_related_items(context, name):

    category_data = {"title": name}
    response = requests.post(f"{BASE_URL}/categories", json=category_data)
    assert response.status_code == 201, f"Failed to create category: {response.status_code}"
    context.category = response.json()

    todo_data = {"title": f"Todo for {name}", "description": "Sample related todo"}
    response = requests.post(f"{BASE_URL}/todos", json=todo_data)
    assert response.status_code == 201, f"Failed to create todo: {response.status_code}"
    todo_id = response.json()['id']

    project_data = {"title": f"Project for {name}", "description": "Sample related project"}
    response = requests.post(f"{BASE_URL}/projects", json=project_data)
    assert response.status_code == 201, f"Failed to create project: {response.status_code}"
    project_id = response.json()['id']

    response = requests.post(f"{BASE_URL}/categories/{context.category['id']}/todos", json={"id": todo_id})
    assert response.status_code == 201, f"Failed to link todo to category: {response.status_code}"

    response = requests.post(f"{BASE_URL}/categories/{context.category['id']}/projects", json={"id": project_id})
    assert response.status_code == 201, f"Failed to link project to category: {response.status_code}"

    context.related_todo_id = todo_id
    context.related_project_id = project_id


@then('the response should include related items for category "{name}"')
def step_check_related_items(context, name):

    assert context.response.status_code == 200, f"Failed to retrieve category: got status {context.response.status_code}"

    category_id = context.response.json()['categories'][0]['id']

    todos_response = requests.get(f"{BASE_URL}/categories/{category_id}/todos")
    assert todos_response.status_code == 200, "Failed to get related todos"
    todos = todos_response.json()
    assert len(todos) > 0, f"No related todos found for category '{name}'"
    assert context.related_todo_id in [todo['id'] for todo in todos['todos']], "Expected todo not found in related items"

    projects_response = requests.get(f"{BASE_URL}/categories/{category_id}/projects")
    assert projects_response.status_code == 200, "Failed to get related projects"
    projects = projects_response.json()
    assert len(projects) > 0, f"No related projects found for category '{name}'"
    assert context.related_project_id in [project['id'] for project in projects['projects']], "Expected project not found in related items"

@then('the category name should be "{name}"')
def step_check_category_name(context, name):
    category = context.response.json()
    assert category['categories'][0]['title'] == name, f"Expected category name '{name}', but got '{category['name']}'"

# Error Flow
@when('the user retrieves the category with id "{invalid_id}"')
def step_retrieve_non_existent_category(context, invalid_id):
    response = requests.get(f"{BASE_URL}/categories/{invalid_id}")
    context.response = response
    print(f"Response: {context.response.json()}")

@then("the system should respond with status code 404")
def step_validate_404_status(context):
    assert context.response.status_code == 404, (
        f"Expected status code 404 but got {context.response.status_code}"
    )

@then('category the user should receive an error message {invalid_id} category')
def step_validate_error_message(context, invalid_id):
    error_message = context.response.json().get("errorMessages", "")
    expected_message = f"Could not find an instance with categories/{invalid_id}"

    assert expected_message in error_message, (
        f"Expected error message '{expected_message}', but got '{error_message}'"
    )
