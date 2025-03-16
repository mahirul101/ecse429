from behave import given, when, then
import requests

BASE_URL = "http://localhost:4567"

def project_exists(project_id):
    response = requests.get(f"{BASE_URL}/projects/{project_id}")
    return response.status_code == 200

@given('the server is running')
def step_server_running(context):
    response = requests.get(BASE_URL)
    assert response.status_code in [200, 404], "Server is not running or reachable"

@given('the following projects exist')
def step_projects_exist(context):
    for row in context.table:
        project_data = {
            "title": row["title"],
            "description": row.get("description", ""),
            "active": row.get("active", "true")  # Default active to true
        }
        response = requests.post(f"{BASE_URL}/projects", json=project_data)
        assert response.status_code in [201, 409]  # 201 Created, 409 Conflict (if project already exists)

@given('the project with id "{project_id}" is linked to tasks and categories')
def step_project_has_relations(context, project_id):
    """Assume a project has tasks or categories linked for alternate flow."""
    # Mock the presence of linked tasks and categories (could use actual API calls)
    assert project_exists(project_id), f"Project {project_id} does not exist"

@when('the user deletes the project with id "{project_id}"')
def step_delete_project(context, project_id):
    response = requests.delete(f"{BASE_URL}/projects/{project_id}")
    context.response = response

@then('the project with id "{project_id}" should no longer exist in the system')
def step_verify_project_deleted(context, project_id):
    response = requests.get(f"{BASE_URL}/projects/{project_id}")
    assert response.status_code == 404, f"Project {project_id} was not deleted"

@then('the user receives a confirmation message "{message}"')
def step_confirm_deletion(context, message):
    assert context.response.status_code == 200, "Unexpected response status"
    assert message in context.response.text, "Expected confirmation message not found"

@then('the project with id "{project_id}" and its associations should be removed from the system')
def step_verify_project_and_relations_deleted(context, project_id):
    response = requests.get(f"{BASE_URL}/projects/{project_id}")
    assert response.status_code == 404, f"Project {project_id} or its associations were not deleted"

@when('the user attempts to delete a project with id "{invalid_project_id}"')
def step_attempt_delete_non_existent_project(context, invalid_project_id):
    response = requests.delete(f"{BASE_URL}/projects/{invalid_project_id}")
    context.response = response

@then('the user should receive an error message "Project not found for id {invalid_project_id}"')
def step_verify_delete_error(context, invalid_project_id):
    assert context.response.status_code == 404, "Expected 404 error"
    assert f"Project not found for id {invalid_project_id}" in context.response.text
