from behave import *
import requests
import json

# Base URL and endpoints
base_url = "http://localhost:4567"
projects_endpoint = f"{base_url}/projects"
categories_endpoint = f"{base_url}/categories"

# Helper functions for debugging
def print_response(response):
    print(f"Status Code: {response.status_code}")
    print(f"Response Body: {response.text}")

# Helper function to get project by title
def get_project_by_title(title):
    response = requests.get(projects_endpoint)
    if response.status_code == 200:
        projects = response.json().get('projects', [])
        for project in projects:
            if project['title'] == title:
                return project
    return None

# Helper function to get category by title
def get_category_by_title(title):
    response = requests.get(categories_endpoint)
    if response.status_code == 200:
        categories = response.json().get('categories', [])
        for category in categories:
            if category['title'] == title:
                return category
    return None

# Helper function to assign a category to a project
def assign_category_to_project(category_id, project_id):
    url = f"{projects_endpoint}/{project_id}/categories"
    payload = {"id": category_id}
    response = requests.post(url, json=payload)
    return response.status_code == 201

@given('the category "{category_title}" is assigned to project "{project_id}"')
def step_impl_assign_category(context, category_title, project_id):
    category_id = context.category_ids[category_title]
    assert assign_category_to_project(category_id, project_id)

@when('removing category "{category_title}" from project "{project_id}"')
def step_impl_remove_category(context, category_title, project_id):
    category_id = context.category_ids[category_title]
    url = f"{projects_endpoint}/{project_id}/categories/{category_id}"
    context.response = requests.delete(url)
    print_response(context.response)

@then('the category "{category_title}" should not be assigned to project "{project_id}"')
def step_impl_verify_category_not_assigned(context, category_title, project_id):
    category_id = context.category_ids[category_title] if category_title in context.category_ids else "invalid"
    url = f"{projects_endpoint}/{project_id}/categories"
    response = requests.get(url)
    assert response.status_code == 200
    categories = response.json().get('categories', [])
    category_ids = [category['id'] for category in categories]
    assert category_id not in category_ids

@then('the system should respond with status code 200')
def step_impl_verify_status_code_200(context):
    assert context.response.status_code == 200

@when('attempting to remove category "{category_title}" from project "{project_id}"')
def step_impl_attempt_remove_category(context, category_title, project_id):
    category_id = context.category_ids[category_title] if category_title in context.category_ids else "invalid"
    url = f"{projects_endpoint}/{project_id}/categories/{category_id}"
    context.response = requests.delete(url)
    print_response(context.response)

@then('receive project removal error "{error_code}"')
def step_impl_verify_project_removal_error(context, error_code):
    # print_response(context.response)
    error_code = int(error_code)
    assert context.response.status_code == error_code # bug, should be 404

@given('the category "{category_title}" is not assigned to project "{project_id}"')
def step_impl_category_not_assigned(context, category_title, project_id):
    category_id = context.category_ids[category_title]
    url = f"{projects_endpoint}/{project_id}/categories/{category_id}"
    response = requests.delete(url)
    assert response.status_code in [200, 404]  # Either already removed or not assigned