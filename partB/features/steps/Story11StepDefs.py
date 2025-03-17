from behave import *
import requests

# Base URL and endpoints
base_url = "http://localhost:4567"
projects_endpoint = f"{base_url}/projects"

# Helper function to get project by ID
def get_project_by_id(project_id):
    response = requests.get(f"{projects_endpoint}/{project_id}")
    if response.status_code == 200 and response.json().get('projects'):
        return response.json()['projects'][0]
    return None

# Helper function to create a project with a specific ID
def create_project_with_id(project_id, title, completed=False, active=True, description=""):
    payload = {
        "id": project_id,
        "title": title,
        "completed": completed,
        "active": active,
        "description": description
    }
    response = requests.post(projects_endpoint, json=payload)
    return response.json().get('id')

@given('existing project')
def step_impl_existing_project(context):
    for row in context.table:
        project_id = row['id']
        project = get_project_by_id(project_id)
        if not project:
            project_id = create_project_with_id(
                project_id=project_id,
                title=row['title'],
                completed=row['completed'].lower() == 'true',
                active=row['active'].lower() == 'true',
                description=row['description']
            )
        context.project_id = project_id

@when('updating project "{project_id}" completed status to "{completed}"')
def step_impl_update_completed(context, project_id, completed):
    url = f"{projects_endpoint}/{project_id}"
    payload = {
        "completed": completed.lower() == 'true'
    }
    context.response = requests.put(url, json=payload)
    assert context.response.status_code == 200

@then('project "{project_id}" shows completed status "{completed}"')
def step_impl_verify_completed(context, project_id, completed):
    response = requests.get(f"{projects_endpoint}/{project_id}")
    assert response.status_code == 200
    assert str(response.json()['projects'][0]['completed']).lower() == completed.lower()

@when('updating project "{project_id}" with title "{title}" description to "{new_desc}"')
def step_impl_update_description(context, project_id, title, new_desc):
    url = f"{projects_endpoint}/{project_id}"
    payload = {
        "title": title,
        "description": new_desc
    }
    context.response = requests.put(url, json=payload)
    assert context.response.status_code == 200

@then('project "{project_id}" description matches "{new_desc}"')
def step_impl_verify_description(context, project_id, new_desc):
    response = requests.get(f"{projects_endpoint}/{project_id}")
    assert response.status_code == 200
    assert response.json()['projects'][0]['description'] == new_desc

@when('attempting to update project "{invalid_id}"')
def step_impl_attempt_update_invalid(context, invalid_id):
    url = f"{projects_endpoint}/{invalid_id}"
    payload = {
        "title": "Invalid Project",
        "completed": "true"
    }
    context.response = requests.put(url, json=payload)

@then('receive project update error "{error_message}"')
def step_impl_verify_error(context, error_message):
    assert context.response.status_code == 404
    actual_error = context.response.json().get('errorMessages', [''])[0]
    assert error_message in actual_error