from behave import given, when, then
import requests
import json

BASE_URL = "http://localhost:4567"

@given("the system is reset to its initial state")
def step_reset_system(context):
    response = requests.get(f"{BASE_URL}/categories")
    if response.status_code == 200:
        categories = json.loads(response.text).get("categories", [])
        for category in categories:
            requests.delete(f"{BASE_URL}/categories/{category['id']}")

    context.existing_categories = set()


@when('the user creates a new category with name "{name}" and description "{description}"')
def step_create_category(context, name, description):
    category_data = {"title": name, "description": description}
    response = requests.post(f"{BASE_URL}/categories", json=category_data)
    context.response = response
    context.new_category = {"name": name, "description": description}

@then("the system should respond with status code 201 and generate a new category id")
def step_validate_category_created(context):
    assert context.response.status_code == 201, "Expected status 201 but got {}".format(context.response.status_code)
    response_data = json.loads(context.response.text)
    assert "id" in response_data, "Category ID not generated"


@then('the category with name "{name}" and description "{description}" should be present in the system')
def step_validate_category_exists(context, name, description):
    response = requests.get(f"{BASE_URL}/categories")
    assert response.status_code == 200, "Failed to retrieve categories"

    categories = json.loads(response.text).get("categories", [])
    found = any(cat["title"] == name and cat["description"] == description for cat in categories)
    assert found, f"Category '{name}' with description '{description}' not found"

@then('the category with name "{name}" should be successfully created again')
def step_validate_category_exists(context, name):
    response = requests.get(f"{BASE_URL}/categories")
    assert response.status_code == 200, "Failed to retrieve categories"

    categories = json.loads(response.text).get("categories", [])
    count = sum(1 for cat in categories if cat["title"] == name)

    assert count == 2, f"Expected 2 categories with name '{name}', but found {count}"

@then('the user receives a confirmation message "Category created successfully"')
def step_validate_success_message(context):
    assert context.response.status_code == 201, "Category was not created successfully"

@given('a category with name "{name}" already exists')
def step_create_duplicate_category(context, name):
    if name in context.existing_categories:
        return
    category_data = {"title": name, "description": "Cool category"}
    response = requests.post(f"{BASE_URL}/categories", json=category_data)
    assert response.status_code == 201, f"Failed to create category {name}"

    context.existing_categories.add(name)

@then("the system should respond with status code 400")
def step_validate_bad_request(context):
    assert context.response.status_code == 400, "Expected status 400 but got {}".format(context.response.status_code)

@when('the user attempts to create a new category with name {name} and description {description}')
def step_attempt_create_invalid_category(context, name, description):
    category_data = {}
    name = name.strip('""')
    description = description.strip('""')
    if name:
        category_data["title"] = name
        category_data["description"] = description
    response = requests.post(f"{BASE_URL}/categories", json=category_data)
    context.response = response

@then('the user should receive an error message {missing_field}')
def step_validate_missing_field_error(context, missing_field):
    response_data = json.loads(context.response.text)
    assert "errorMessages" in response_data, "Expected error message but none found"
    expected_message =  missing_field.strip('"')+" : field is mandatory"
    message_got = response_data["errorMessages"][0]
    assert expected_message in message_got, f"Unexpected error message: {response_data['errorMessages']}"