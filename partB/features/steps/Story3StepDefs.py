from behave import given, when, then
import requests

BASE_URL = "http://localhost:4567"

@given('existing TODO')
def step_impl(context):
    for row in context.table:
        payload = {
            "title": row['title'],
            "doneStatus": row['doneStatus'].lower() == 'true'
        }
        response = requests.post(f"{BASE_URL}/todos", json=payload)
        assert response.status_code == 201

@when('updating todo "{todo_id}" doneStatus to {status}')
def step_impl(context, todo_id, status):
    payload = {"doneStatus": status.lower() == 'true'}
    response = requests.put(f"{BASE_URL}/todos/{todo_id}", json=payload)
    context.response = response

@then('todo "{todo_id}" shows doneStatus {status}')
def step_impl(context, todo_id, status):
    response = requests.get(f"{BASE_URL}/todos/{todo_id}")
    assert response.status_code == 200
    todo = response.json()['todos'][0]
    assert todo['doneStatus'] == str(status.lower() == 'true').lower()

@when('updating todo "{todo_id}" with title "{title}" description to "{new_desc}"')
def step_impl(context, todo_id, title, new_desc):
    payload = {"title": title, "description": new_desc}
    response = requests.put(f"{BASE_URL}/todos/{todo_id}", json=payload)
    context.response = response

@then('todo "{todo_id}" description matches "{new_desc}"')
def step_impl(context, todo_id, new_desc):
    response = requests.get(f"{BASE_URL}/todos/{todo_id}")
    assert response.status_code == 200
    todo = response.json()['todos'][0]
    assert todo['description'] == new_desc

@when('attempting to update todo "{invalid_id}"')
def step_impl(context, invalid_id):
    payload = {"description": "Invalid update"}
    response = requests.put(f"{BASE_URL}/todos/{invalid_id}", json=payload)
    context.response = response

@then('receive todo update error "Invalid GUID for {invalid_id} entity todo"')
def step_impl(context, invalid_id):
    assert context.response.status_code == 404
    expected_error = f"Invalid GUID for {invalid_id} entity todo"
    actual_error = context.response.json().get('errorMessages', [''])[0]
    assert expected_error in actual_error