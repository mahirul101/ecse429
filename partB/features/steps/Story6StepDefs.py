from behave import given, when, then
import requests
import json

BASE_URL = "http://localhost:4567"

@given('the following projects exist')
def step_projects_exist(context):
    context.projects = {}
    for row in context.table:
        project_data = {
            "title": row["title"],
            "description": row.get("description", ""),
            "active": row.get("active", "True") == "True"
        }
        response = requests.post(f"{BASE_URL}/projects", json=project_data)
        assert response.status_code == 201, f"Failed to create project {row['title']}"
        context.projects[row["title"]] = json.loads(response.text)["id"]

@given('the project with title "{title}" has tasks associated with it')
def step_project_has_tasks(context, title):
    project_id = context.projects.get(title)
    assert project_id, f"Project with title '{title}' not found"

    todo_data = {"title": f"Task for {title}", "description": f"Task for {title}"}
    response = requests.post(f"{BASE_URL}/todos", json=todo_data)
    assert response.status_code == 201
    todo_id = json.loads(response.text).get("id")
    
    response = requests.post(f"{BASE_URL}/todos/{todo_id}/tasksof", json={"id": project_id})
    assert response.status_code == 201
    
    if not hasattr(context, 'todos_by_project'):
        context.todos_by_project = {}

    if project_id not in context.todos_by_project:
        context.todos_by_project[project_id] = []

    context.todos_by_project[project_id].append(todo_id)

@given('the project with title "{title}" has categories associated with it')
def step_project_has_categories(context, title):
    project_id = context.projects.get(title)
    assert project_id, f"Project with title '{title}' not found"
    
    category_data = {"title": f"Category for {title}", "description": f"Category for {title}"}
    response = requests.post(f"{BASE_URL}/categories", json=category_data)
    assert response.status_code == 201
    category_id = json.loads(response.text).get("id")
    
    response = requests.post(f"{BASE_URL}/categories/{category_id}/projects", json={"id": project_id})
    assert response.status_code == 201
    
    if not hasattr(context, 'categories_by_project'):
        context.categories_by_project = {}

    if project_id not in context.categories_by_project:
        context.categories_by_project[project_id] = []

    context.categories_by_project[project_id].append(category_id)

@when('the user deletes the project with id "{title}"')
def step_delete_project(context, title):
    project_id = context.projects.get(title)
    assert project_id, f"Project with title '{title}' not found"
    response = requests.delete(f"{BASE_URL}/projects/{project_id}")
    assert response.status_code == 200, f"Failed to delete project {title}"
    context.deleted_project_id = project_id

@when('the user attempts to delete a project with id "{invalid_project_id}"')
def step_delete_nonexistent_project(context, invalid_project_id):
    response = requests.delete(f"{BASE_URL}/projects/{invalid_project_id}")
    context.response = response

@then('the project with id "{title}" should no longer exist in the system')
def step_verify_project_deleted(context, title):
    project_id = context.projects.get(title)
    response = requests.get(f"{BASE_URL}/projects/{project_id}")
    assert response.status_code == 404, f"Project {title} still exists"

@then('the relationships between the project and its tasks should be removed')
def step_verify_task_relationships_removed(context):
    deleted_project_id = context.deleted_project_id
    for todo_id in context.todos_by_project.get(deleted_project_id, []):
        response = requests.get(f"{BASE_URL}/todos/{todo_id}/tasksof/{deleted_project_id}")
        assert response.status_code in [404, 200]
        if response.status_code == 200:
            assert not json.loads(response.text), "Tasks are still linked to the deleted project"

@then('the relationships between the project and its categories should be removed')
def step_verify_category_relationships_removed(context):
    deleted_project_id = context.deleted_project_id
    for category_id in context.categories_by_project.get(deleted_project_id, []):
        response = requests.get(f"{BASE_URL}/categories/{category_id}/projects/{deleted_project_id}")
        assert response.status_code in [404, 200]
        if response.status_code == 200:
            assert not json.loads(response.text), "Categories are still linked to the deleted project"

@then('the user should receive an error message "Project not found for id {invalid_project_id}"')
def step_verify_error_message(context, invalid_project_id):
    assert context.response.status_code == 404, "Expected 404 error"
    response_json = json.loads(context.response.text)
    assert response_json["errorMessages"][0] == f"Could not find any instances with projects/{invalid_project_id}", "Error message mismatch"