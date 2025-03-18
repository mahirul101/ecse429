from behave import given, when, then
import requests

BASE_URL = "http://localhost:4567"
CATEGORIES_ENDPOINT = f"{BASE_URL}/categories"
PROJECTS_ENDPOINT = f"{BASE_URL}/projects"

def get_category_id_by_name(title):
    response = requests.get(CATEGORIES_ENDPOINT)
    if response.status_code == 200:
        categories = response.json().get("categories", [])
        for category in categories:
            if category["title"] == title:
                return category["id"]
    return None

# Helper function to get project IDs under a category
def get_projects_by_category(category_id):
    response = requests.get(f"{CATEGORIES_ENDPOINT}/{category_id}/projects")
    if response.status_code == 200:
        return response.json().get("projects", [])
    return None

@given('the following categories exist retreived from the API')
def step_create_categories(context):
    """Ensure categories exist before running tests."""
    context.category_ids = {}
    for row in context.table:
        title = row["title"]

        # Check if category already exists
        category_id = get_category_id_by_name(title)
        if category_id:
            print(f"✅ Category '{title}' already exists with ID {category_id}")
            context.category_ids[title] = category_id
            continue

        # Create category
        response = requests.post(CATEGORIES_ENDPOINT, json={"title": title})
        assert response.status_code == 201, f"❌ Failed to create category '{title}': {response.text}"
        category_id = response.json()["id"]
        context.category_ids[title] = category_id
        print(f"✅ Created Category '{title}' with ID {category_id}")

@given('the following projects exist under category {category_name}')
def step_create_projects_under_category(context, category_name):
    """Ensure projects exist and are linked to a category."""
    category_id = context.category_ids.get(category_name)
    assert category_id, f"❌ Category '{category_name}' does not exist."

    context.project_ids = {}
    for row in context.table:
        title = row["title"]
        value = row["active"].lower()
        active = value == "true"
        print(f"The active value is: {active}")
        print(f"The value is: {value}")

        # Create project
        response = requests.post(PROJECTS_ENDPOINT, json={"title": title, "active": active})
        assert response.status_code == 201, f"❌ Failed to create project '{title}': {response.text}"
        project_id = response.json()["id"]
        context.project_ids[title] = project_id

        # Link project to category
        response = requests.post(f"{CATEGORIES_ENDPOINT}/{category_id}/projects", json={"id": project_id})
        assert response.status_code == 201, f"❌ Failed to link project '{title}' to category '{category_name}': {response.text}"
        print(f"✅ Linked Project '{title}' to Category '{category_name}'")

@given('category "{category_name}" exists but has no projects')
def step_category_exists_without_projects(context, category_name):
    """Ensure a category exists without any projects."""
    category_id = get_category_id_by_name(category_name)
    if not category_id:
        response = requests.post(CATEGORIES_ENDPOINT, json={"title": category_name})
        assert response.status_code == 201, f"❌ Failed to create category '{category_name}': {response.text}"
        category_id = response.json()["id"]
    
    context.category_ids[category_name] = category_id
    print(f"✅ Category '{category_name}' exists but has no projects")

@when('retrieving projects under category "{category_name}"')
def step_retrieve_projects_by_category(context, category_name):
    """Retrieve projects associated with a category."""
    category_id = context.category_ids.get(category_name)
    print(f"The category id is: {category_id}")
    if category_id is not None:
        assert category_id, f"❌ Category '{category_name}' does not exist in context."

    response = requests.get(f"{CATEGORIES_ENDPOINT}/{category_id}/projects")
    context.response = response
    print(f"📥 Retrieved projects for category '{category_name}' (Status: {response.status_code})")

@then('the system should respond with status code {status_code:d} retreive projects')
def step_verify_status_code(context, status_code):
    assert context.response.status_code == status_code, f"❌ Expected {status_code}, got {context.response.status_code}"

@then('the response should contain the following projects')
def step_verify_response_contains(context):
    """Verify that the expected projects exist in the response."""
    response_data = context.response.json().get("projects", [])
    expected_projects = {row["title"]: row["active"].lower() == "true" for row in context.table}

    # Extract projects from response
    actual_projects = {project["title"]: project["active"].lower() == "true" for project in response_data}

    assert expected_projects == actual_projects, f"❌ Expected {expected_projects}, got {actual_projects}"
    print(f"✅ Retrieved correct projects: {actual_projects}")

@then('the response should be an empty list of projects')
def step_verify_empty_response(context):
    """Ensure the API returns an empty list when no projects exist in the category."""
    projects = context.response.json().get("projects", [])
    assert projects == [], f"❌ Expected empty list, got {projects}"
    print(f"✅ Retrieved empty project list as expected.")

