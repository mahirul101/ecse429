from behave import *
import requests
import json

base_url = "http://localhost:4567"
projects_endpoint = f"{base_url}/projects"
todos_endpoint = f"{base_url}/todos"

# Helper functions
def get_project_id_by_title(context, title):
    print(f"Getting project id for {title}")
    response = requests.get(f"{projects_endpoint}?title={title}")
    print(response.json())
    if response.status_code == 200 and response.json().get('projects'):
        return response.json()['projects'][0]['id']
    return None

def get_todo_id_by_title(context, title):
    print(f"Getting todo id for {title}")
    response = requests.get(f"{todos_endpoint}?title={title}")
    print(response.json())
    if response.status_code == 200 and response.json().get('todos'):
        return response.json()['todos'][0]['id']
    return None

def create_project(title):
    payload = {"title": title}
    response = requests.post(projects_endpoint, json=payload)
    return response.json().get('id')

def create_todo(title, description):
    payload = {
        "title": title,
        "description": description
    }
    response = requests.post(todos_endpoint, json=payload)
    print(response.json())
    return response.json().get('id')

# Step implementations
@given('a project with title "{title}" exists')
def step_impl(context, title):
    project_id = get_project_id_by_title(context, title)
    if not project_id:
        project_id = create_project(title)
    context.project_id = project_id

@given('TODOs with the following details exist')
def step_impl(context):
    for row in context.table:
        todo_id = get_todo_id_by_title(context, row['title'])
        if not todo_id:
            print(f"Creating todo: {row['title']}")
            create_todo(row['title'], row['description'])

@when('adding todo "{todo_title}" to project "{project_title}" tasks')
def step_impl(context, todo_title, project_title):
    todo_id = get_todo_id_by_title(context, todo_title)
    print(f"Adding todo {todo_title} to project {project_title}")
    project_id = get_project_id_by_title(context, project_title)
    
    url = f"{projects_endpoint}/{project_id}/tasks"
    print(f"Adding todo {todo_id} to project {project_id}")
    payload = {"id": todo_id}
    context.response = requests.post(url, json=payload)

@when('creating new todo "{new_title}" with description "{desc}"')
def step_impl(context, new_title, desc):
    payload = {
        "title": new_title,
        "description": desc
    }
    response = requests.post(todos_endpoint, json=payload)
    context.new_todo_id = response.json().get('id')

@when('adding it to project "{project_title}" tasks')
def step_impl(context, project_title):
    project_id = get_project_id_by_title(context, project_title)
    url = f"{projects_endpoint}/{project_id}/tasks"
    payload = {"id": context.new_todo_id}
    context.response = requests.post(url, json=payload)

@then('the project tasks include "{todo_title}"')
def step_impl(context, todo_title):
    project_id = context.project_id
    response = requests.get(f"{projects_endpoint}/{project_id}/tasks")
    print(response.json())
    tasks = [task['title'] for task in response.json().get('todos', [])]
    assert todo_title in tasks

@then('the response status is {status_code:d}')
def step_impl(context, status_code):
    assert context.response.status_code == status_code

@when('attempting to add non-existent todo "{invalid_id}" to project')
def step_impl(context, invalid_id):
    project_id = context.project_id
    url = f"{projects_endpoint}/{project_id}/tasks"
    payload = {"id": invalid_id}
    context.response = requests.post(url, json=payload)

@then('receive error "{error_message}"')
def step_impl(context, error_message):
    actual_error = context.response.json().get('errorMessages', [''])[0]
    assert error_message in actual_error