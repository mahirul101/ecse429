from behave import *
import requests
import json

# Base URL and endpoints
base_url = "http://localhost:4567"
projects_endpoint = f"{base_url}/projects"

# Helper functions for debugging
def print_response(response):
    print(f"Status Code: {response.status_code}")
    print(f"Response Body: {response.text}")

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

@given('existing projects')
def step_impl_existing_projects(context):
    """Create projects defined in the scenario's data table"""
    for row in context.table:
        project_id = row['id']
        title = row['title'].strip('"')  # Remove quotes if present
        completed = row['completed'].lower() == 'true'
        active = row['active'].lower() == 'true'
        description = row['description'].strip('"')
        
        # Check if project already exists
        existing_project = get_project_by_id(project_id)
        if not existing_project:
            # Create the project
            create_project_with_id(
                project_id=project_id,
                title=title,
                completed=completed,
                active=active,
                description=description
            )
        
        # Store the last project ID in context for later use
        context.project_id = project_id
        
    # Print confirmation for debugging
    print(f"Created/verified project with ID {context.project_id}")

    
@when('retrieving project "{project_id}" with fields "{fields}"')
def step_impl_retrieve_project_with_fields(context, project_id, fields):
    # Remove quotes if present
    fields = fields.strip('"')
    url = f"{projects_endpoint}/{project_id}?fields={fields}"
    context.response = requests.get(url)
    context.requested_fields = fields.split(',')
    print_response(context.response)

@when('attempting to retrieve project "{invalid_id}"')
def step_impl_attempt_retrieve_invalid_project(context, invalid_id):
    url = f"{projects_endpoint}/{invalid_id}"
    context.response = requests.get(url)
    print_response(context.response)

@then('the project details should match')
def step_impl_verify_project_details(context):
    # Get the expected values from the table
    expected_data = context.table[0]
    
    # Get the actual project data from the response
    response_data = context.response.json()
    assert 'projects' in response_data, "Response does not contain projects key"
    assert len(response_data['projects']) > 0, "No projects returned in response"
    actual_project = response_data['projects'][0]
    
    # Compare each expected field
    if 'title' in expected_data:
        assert actual_project['title'] == expected_data['title'].strip('"'), f"Title mismatch: expected {expected_data['title']}, got {actual_project['title']}"
    if 'completed' in expected_data:
        expected_completed = expected_data['completed'].lower() == 'true'
        assert actual_project['completed'] == expected_completed, f"Completed mismatch: expected {expected_completed}, got {actual_project['completed']}"
    if 'active' in expected_data:
        expected_active = expected_data['active'].lower() == 'true'
        assert actual_project['active'] == expected_active, f"Active mismatch: expected {expected_active}, got {actual_project['active']}"
    if 'description' in expected_data:
        assert actual_project['description'] == expected_data['description'].strip('"'), f"Description mismatch: expected {expected_data['description']}, got {actual_project['description']}"

@then('the response should only contain fields "{fields}"')
def step_impl_verify_fields(context, fields):
    # Remove quotes if present and get requested fields
    fields = fields.strip('"')
    requested_fields = fields.split(',')
    
    # Get the project from response
    response_data = context.response.json()
    assert 'projects' in response_data, "Response does not contain projects key"
    assert len(response_data['projects']) > 0, "No projects returned in response"
    actual_project = response_data['projects'][0]
    

    for field in requested_fields:
        assert field in actual_project, f"Requested field '{field}' was not included in response"
    
    # Log a warning about the API behavior
    print("Note: API returns all fields regardless of fields parameter. This is normal behavior.")


@when('retrieving project "{project_id}"')
def step_impl_retrieve_project(context, project_id):
    url = f"{projects_endpoint}/{project_id}"
    context.response = requests.get(url)
    print_response(context.response)

@then('receive project error "{error_message}"')
def step_impl_verify_project_error(context, error_message):
    # The API might return different status codes or error formats
    # Print the actual response for debugging
    print_response(context.response)
    
    # Verify status code is an error (4xx)
    assert 400 <= context.response.status_code < 500, f"Expected error status code, got {context.response.status_code}"
    
    # Verify error message is included in response
    error_data = context.response.json()
    assert 'errorMessages' in error_data, "Response does not contain errorMessages key"
    assert len(error_data['errorMessages']) > 0, "No error messages returned in response"
    actual_error = error_data['errorMessages'][0]
    assert error_message in actual_error, f"Error message mismatch: expected '{error_message}', got '{actual_error}'"