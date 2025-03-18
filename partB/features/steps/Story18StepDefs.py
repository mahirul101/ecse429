from behave import *
import requests

BASE_URL = "http://localhost:4567"
PROJECTS_ENDPOINT = f"{BASE_URL}/projects"
TODOS_ENDPOINT = f"{BASE_URL}/todos"

# Helper function to print response details for debugging
def print_response(response):
    print(f"Status Code: {response.status_code}")
    print(f"Response Body: {response.text}")

@given('existing projects with title and active status')
def step_impl_existing_projects(context):
    """Ensure the projects defined in the scenario's data table exist."""
    context.project_ids = {}
    for row in context.table:
        title = row['title'].strip('"')
        active = row['active'].lower() == 'true'

        # Check if the project already exists
        response = requests.get(PROJECTS_ENDPOINT)
        if response.status_code == 200:
            projects = response.json().get("projects", [])
            existing_project = next((project for project in projects if project['title'] == title), None)
            if existing_project:
                print(f"Project '{title}' already exists with ID {existing_project['id']}")
                context.project_ids[title] = existing_project['id']
                continue

        # Create the project
        payload = {"title": title, "active": active}
        response = requests.post(PROJECTS_ENDPOINT, json=payload)
        assert response.status_code == 201, f"Failed to create project: {response.text}"
        project_id = response.json().get("id")
        context.project_ids[title] = project_id
        print(f"Created Project '{title}' with ID {project_id}")

@given('the to-do "{todo_title}" is assigned to project "{project_title}"')
def step_impl_assign_todo_to_project(context, todo_title, project_title):
    """Assign a to-do to a project."""
    todo_id = context.todo_ids.get(todo_title)
    assert todo_id, f"To-Do '{todo_title}' does not exist in context."
    project_id = context.project_ids.get(project_title)
    assert project_id, f"Project '{project_title}' does not exist in context."

    # Assign the to-do to the project
    url = f"{PROJECTS_ENDPOINT}/{project_id}/tasks"
    payload = {"id": todo_id}
    response = requests.post(url, json=payload)
    assert response.status_code == 201, f"Failed to assign to-do to project: {response.text}"
    print(f"Assigned To-Do '{todo_title}' to Project '{project_title}'")

@when('retrieving to-dos from project "{project_title}"')
def step_impl_retrieve_todos_from_project(context, project_title):
    """Retrieve to-dos from a specific project."""
    url = f"{PROJECTS_ENDPOINT}/{project_title}/tasks"
    context.response = requests.get(url)
    print_response(context.response)

@when('retrieving to-dos from invalid project "{project_title}"')
def step_impl_retrieve_todos_from_invalid_project(context, project_title):
    """Retrieve to-dos from an invalid project."""
    project_id = context.project_ids.get(project_title)
    assert not project_id, f"Project '{project_title}' exists in context."
    url = f"{PROJECTS_ENDPOINT}/{project_id}/tasks"
    context.response = requests.get(url)
    print_response(context.response)