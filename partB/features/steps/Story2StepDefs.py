from behave import given, when, then
import requests

BASE_URL = "http://localhost:4567"

def get_project_id_by_title(title):
    response = requests.get(f"{BASE_URL}/projects")
    projects = response.json()["projects"]
    for project in projects:
        if project["title"] == title:
            return project["id"]
    return None

def get_category_id_by_title(title):
    response = requests.get(f"{BASE_URL}/categories")
    categories = response.json()["categories"]
    for category in categories:
        if category["title"] == title:
            return category["id"]
    return None

@given('projects exist')
def step_impl(context):
    for row in context.table:
        response = requests.post(f"{BASE_URL}/projects", json={"title": row['title']})
        assert response.status_code == 201

@given('category "Subject: {subject}" exists')
def step_impl(context, subject):
    response = requests.post(f"{BASE_URL}/categories", json={"title": subject})
    assert response.status_code == 201

@when('assigning "{subject}" category to "{project}" project')
def step_impl(context, subject, project):
    context.subject = subject
    project_id = get_project_id_by_title(project)
    category_id = get_category_id_by_title(subject)
    response = requests.post(f"{BASE_URL}/projects/{project_id}/categories", json={"id": category_id})
    assert response.status_code == 201

@then('"{project}" appears in "{subject}" category projects')
def step_impl(context, project, subject):
    project_id = get_project_id_by_title(project)
    category_id = get_category_id_by_title(subject)
    
    # Check if the category is assigned to the project
    response = requests.get(f"{BASE_URL}/projects/{project_id}/categories")
    assert response.status_code == 200
    categories = response.json()["categories"]
    category_titles = [cat["title"] for cat in categories]
    assert subject in category_titles

@when('creating new category "{subject}"')
def step_impl(context, subject):
    context.subject = subject
    response = requests.post(f"{BASE_URL}/categories", json={"title": subject})
    assert response.status_code == 201

@when('assigning it to "{project}" project')
def step_impl(context, project):
    project_id = get_project_id_by_title(project)
    category_id = get_category_id_by_title(context.subject)
    response = requests.post(f"{BASE_URL}/projects/{project_id}/categories", json={"id": category_id})
    assert response.status_code == 201

@when('attempting to assign "Literature" category to non-existent project "{invalid_id}"')
def step_impl(context, invalid_id):
    category_id = get_category_id_by_title("Literature")
    response = requests.post(f"{BASE_URL}/projects/{invalid_id}/categories", json={"id": category_id})
    context.response = response

@then('receive category assignment error "{error_message}"')
def step_impl(context, error_message):
    assert context.response.status_code == 404
    print(context.response.text)
    assert error_message in context.response.text
