from behave import given, when, then
import requests
import json

BASE_URL = "http://localhost:4567"

@given('the following categories exist in the system')
def step_categories_exist(context):
    categories = [row.as_dict() for row in context.table]
    for category in categories:
        name = category["name"]
        description = category["description"]
        category_data = {"title": name, "description": description}
        response = requests.post(f"{BASE_URL}/categories", json=category_data)
        assert response.status_code == 201, f"Failed to create category {name}"

@given('a category "{name}" exists in the system')
def step_category_exists(context, name):
    response = requests.get(f"{BASE_URL}/categories")
    categories = response.json().get("categories", [])

    category_id = None
    for category in categories:
        if category['title'] == name:
            category_id = category['id']
            break

    if category_id:
        context.category_id = category_id
        response = requests.get(f"{BASE_URL}/categories/{category_id}")
        context.response = response
        assert response.status_code == 200, f"Category {name} not found after lookup"
        print(f"Response: {context.response.json()}")
    else:
        context.response = response

@when('the user deletes the category with name "{name}"')
def step_delete_category_by_name(context, name):
    category_id = context.category_id
    assert category_id, f"Category ID for '{name}' not found"

    response2 = requests.get(f"{BASE_URL}/categories")
    print(f"Response is: {response2.json()}")
    response = requests.delete(f"{BASE_URL}/categories/{category_id}")
    context.response = response
    assert response.status_code == 200, f"Failed to delete category '{name}'"

@then('the category with name "{name}" should no longer exist in the system')
def step_validate_category_deleted(context, name):
    response = requests.get(f"{BASE_URL}/categories")
    assert response.status_code == 200, "Failed to fetch categories"

    categories = response.json().get("categories", [])
    found = any(cat["title"] == name for cat in categories)

    assert not found, f"Category '{name}' still exists after deletion"

@given('a category "{name}" has related items')
def step_category_has_related_items(context, name):

    category_data = {"title": name}
    response = requests.post(f"{BASE_URL}/categories", json=category_data)
    assert response.status_code == 201, f"Failed to create category: {response.status_code}"
    context.category = response.json()
    context.category_id = context.category['id']

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


@then('the category with name {name} should be removed from the system')
def step_validate_category_and_associations_deleted(context, name):
    category_id = context.category_id
    assert category_id, f"Category ID for '{name}' not found"

    # Check if category still exists
    response = requests.get(f"{BASE_URL}/categories/{category_id}")
    assert response.status_code == 404, f"Category '{name}' still exists after deletion"


@when('the user attempts to delete the category with id "{invalid_category_id}" delete category')
def step_attempt_delete_invalid_category(context, invalid_category_id):
    response = requests.delete(f"{BASE_URL}/categories/{invalid_category_id}")
    context.response = response

@then('the system should respond with status code 404 delete category')
def step_validate_404_response(context):
    assert context.response.status_code == 404, f"Expected 404, but got {context.response.status_code}"

@then('the user should receive an error message "Could not find any instances with categories {invalid_category_id}" delete category')
def step_validate_error_message(context, invalid_category_id):
    response_json = context.response.json()
    print(f"Response: {response_json}")
    expected_message = f"Could not find any instances with categories/{invalid_category_id}"
    assert response_json.get("errorMessages")[0] == expected_message, f"Expected '{expected_message}', but got '{response_json.get('errorMessages')[0]}'"
