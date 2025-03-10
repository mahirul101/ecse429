from behave import given, when, then
import requests

BASE_URL = "http://localhost:4567"

@given('the following TODOs exist')
def step_impl(context):
    context.todo_ids = {}
    for row in context.table:
        payload = {
            "title": row['title'],
            "doneStatus": row['doneStatus'].lower() == 'true',
            "description": row['description']
        }
        response = requests.post(f"{BASE_URL}/todos", json=payload)
        assert response.status_code == 201
        todo_id = response.json()['id']
        context.todo_ids[row['title']] = todo_id

@given('the following course todo list projects exist')
def step_impl(context):
    context.project_ids = {}
    for row in context.table:
        payload = {
            "title": row['title'],
            "completed": row['completed'].lower() == 'true',
            "description": row['description'],
            "active": row['active'].lower() == 'true'
        }
        response = requests.post(f"{BASE_URL}/projects", json=payload)
        assert response.status_code == 201
        project_id = response.json()['id']
        context.project_ids[row['title']] = project_id

@when('the student sets the doneStatus {doneStatus} for the TODO with title {title}')
def step_impl(context, doneStatus, title):
    todo_id = context.todo_ids[title]
    payload = {"title": title, "doneStatus": doneStatus.lower() == 'true'}
    response = requests.put(f"{BASE_URL}/todos/{todo_id}", json=payload)
    context.response = response

@then('the TODO with title {title} should have doneStatus {doneStatus}')
def step_impl(context, title, doneStatus):
    todo_id = context.todo_ids[title]
    response = requests.get(f"{BASE_URL}/todos/{todo_id}")
    assert response.status_code == 200
    todo = response.json()['todos'][0]
    assert todo['doneStatus'] == str(doneStatus.lower() == 'true').lower()

@then('the student should be notified of the successful update')
def step_impl(context):
    assert context.response.status_code == 200

@when('a student adds the TODO with title {title} to the course todo list named {course}')
def step_impl(context, title, course):
    todo_id = context.todo_ids[title]
    project_id = context.project_ids[course]
    response = requests.post(f"{BASE_URL}/projects/{project_id}/tasks", json={"id": todo_id})
    context.response = response

@given('a TODO with id {invalid_id} does not exist')
def step_impl(context, invalid_id):
    response = requests.get(f"{BASE_URL}/todos/{invalid_id}")
    assert response.status_code == 404

@when('a student sets the doneStatus {doneStatus} for the TODO with id {non_existing_id}')
def step_impl(context, doneStatus, non_existing_id):
    payload = {"doneStatus": doneStatus.lower() == 'true'}
    response = requests.put(f"{BASE_URL}/todos/{non_existing_id}", json=payload)
    context.response = response

@then('the student should receive an error message {message} for the invalid TODO id {non_existing_id}')
def step_impl(context, message, non_existing_id):
    assert context.response.status_code == 404
    expected_error = f"Invalid GUID for {non_existing_id} entity todo"
    error_messages = context.response.json().get('errorMessages', [''])[0]
    assert expected_error in error_messages