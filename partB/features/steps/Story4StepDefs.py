from behave import given, when, then
import requests

BASE_URL = "http://localhost:4567"

@given('categories exist')
def step_impl(context):
    context.category_ids = {}
    for row in context.table:
        payload = {"title": row['name']}
        response = requests.post(f"{BASE_URL}/categories", json=payload)
        assert response.status_code == 201
        category_id = response.json()['id']
        context.category_ids[row['name']] = category_id

@given('todo "{todo_title}" exists')
def step_impl(context, todo_title):
    context.todo_ids = {}
    payload = {"title": todo_title, "doneStatus": False}
    response = requests.post(f"{BASE_URL}/todos", json=payload)
    assert response.status_code == 201
    context.todo_ids[todo_title] = response.json()['id']

@given('category "{category}" exists')
def step_impl(context, category):
    if category not in context.category_ids:
        payload = {"title": category}
        response = requests.post(f"{BASE_URL}/categories", json=payload)
        assert response.status_code == 201
        context.category_ids[category] = response.json()['id']

@when('assigning "{category}" category to "{todo_title}" todo')
def step_impl(context, category, todo_title):
    todo_id = context.todo_ids[todo_title]
    category_id = context.category_ids[category]
    response = requests.post(f"{BASE_URL}/todos/{todo_id}/categories", json={"id": category_id})
    context.response = response

@then('"{category}" category appears in "{todo_title}" todo')
def step_impl(context, category, todo_title):
    todo_id = context.todo_ids[todo_title]
    response = requests.get(f"{BASE_URL}/todos/{todo_id}/categories")
    assert response.status_code == 200
    categories = response.json()['categories']
    category_titles = [cat['title'] for cat in categories]
    assert category in category_titles

@when('creating a new category "{new_category}"')
def step_impl(context, new_category):
    payload = {"title": new_category}
    response = requests.post(f"{BASE_URL}/categories", json=payload)
    assert response.status_code == 201
    context.category_ids[new_category] = response.json()['id']

@when('assigning it to "{todo_title}" todo')
def step_impl(context, todo_title):
    new_category = list(context.category_ids.keys())[-1]
    todo_id = context.todo_ids[todo_title]
    category_id = context.category_ids[new_category]
    response = requests.post(f"{BASE_URL}/todos/{todo_id}/categories", json={"id": category_id})
    context.response = response

@when('attempting to assign "Homework" category to non-existent todo "{invalid_id}"')
def step_impl(context, invalid_id):
    category_id = context.category_ids['"Homework"']
    response = requests.post(f"{BASE_URL}/todos/{invalid_id}/categories", json={"id": category_id})
    context.response = response