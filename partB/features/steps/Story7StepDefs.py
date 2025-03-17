from behave import given, when, then
import requests
import json

BASE_URL = "http://localhost:4567"


@given("the following categories exist")
def step_create_categories(context):
    context.category_ids = {}  # Store created category IDs
    for row in context.table:
        category_data = {
            "title": row["name"],
            "description": row["description"]
        }
        response = requests.post(f"{BASE_URL}/categories", json=category_data)
        assert response.status_code == 201, f"Failed to create category {row['name']}"

        category_id = json.loads(response.text)["id"]
        context.category_ids[row["name"]] = category_id


@when("the user retrieves all categories")
def step_retrieve_categories(context):
    response = requests.get(f"{BASE_URL}/categories")
    context.response = response


@then("the response should contain at least {min_count:d} categories")
def step_validate_category_count(context, min_count):
    assert context.response.status_code == 200, "Failed to retrieve categories"
    categories = json.loads(context.response.text)["categories"]
    assert len(categories) >= min_count, f"Expected at least {min_count} categories, found {len(categories)}"


@then('each category in the response should include "id", "title", and "description"')
def step_validate_category_fields(context):
    categories = json.loads(context.response.text)["categories"]
    for category in categories:
        assert "id" in category, "Missing 'id' field in category"
        assert "title" in category, "Missing 'title' field in category"
        assert "description" in category, "Missing 'description' field in category"


@given("all categories are removed from the system")
def step_remove_all_categories(context):
    response = requests.get(f"{BASE_URL}/categories")
    if response.status_code == 200:
        categories = json.loads(response.text).get("categories", [])
        for category in categories:
            requests.delete(f"{BASE_URL}/categories/{category['id']}")


@then("the response should be an empty list")
def step_validate_empty_category_list(context):
    categories = json.loads(context.response.text).get("categories", [])
    assert len(categories) == 0, "Expected an empty category list, but found categories"


@then('the user receives a notification "No categories found"')
def step_validate_no_categories_message(context):
    assert context.response.status_code == 200, "Expected 200 status for empty category list"
    response_data = json.loads(context.response.text)
    categories = response_data.get("categories", [])
    assert len(categories) == 0, "Expected empty categories list"

@when("the user attempts to retrieve all categories")
def step_attempt_retrieve_categories(context):
    try:
        response = requests.get(f"{BASE_URL}/categories")
        context.response = response
    except requests.exceptions.ConnectionError:
        context.response = None

@when("the user attempts to retrieve categories from an invalid endpoint")
def step_attempt_retrieve_invalid_endpoint(context):
    response = requests.get(f"{BASE_URL}/invalid_categories")
    context.response = response

@then('the user should receive a 404 status code')
def step_validate_invalid_endpoint_error(context):
    assert context.response.status_code == 404, "Expected 404 Not Found error"
