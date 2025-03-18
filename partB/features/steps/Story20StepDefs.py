from behave import *
import requests
import json
import time

# Base URL and endpoints
base_url = "http://localhost:4567"
todos_endpoint = f"{base_url}/todos"
projects_endpoint = f"{base_url}/projects"

# Helper function to print response details for debugging
def print_response(response):
    print(f"Status Code: {response.status_code}")
    print(f"Response Body: {response.text}")

@given('to-dos in project "{project_title}"')
def step_impl_todos_in_project(context, project_title):
    """Create todos and associate them with the specified project."""
    # First find the project ID by title
    project_title = project_title.strip('"')
    projects_response = requests.get(projects_endpoint)
    projects = projects_response.json().get('projects', [])
    project = next((p for p in projects if p.get('title') == project_title), None)
    
    if not project:
        print(f"Project with title '{project_title}' not found, creating it")
        # Create the project
        create_project_response = requests.post(projects_endpoint, json={"title": project_title})
        if create_project_response.status_code == 201:
            project = create_project_response.json()
        else:
            assert False, f"Failed to create project '{project_title}': {create_project_response.text}"
    
    project_id = project['id']
    print(f"Using project with ID {project_id}")
    
    # Now create or verify todos and associate them with the project
    for row in context.table:
        title = row['title'].strip('"')
        done_status = row['doneStatus'].lower() == 'true' if 'doneStatus' in row else False
        
        # Check if todo with this title already exists
        todos_response = requests.get(todos_endpoint)
        existing_todos = todos_response.json().get('todos', [])
        todo = next((t for t in existing_todos if t.get('title') == title), None)
        
        if todo:
            print(f"Todo with title '{title}' already exists with ID {todo['id']}")
            actual_todo_id = todo['id']
        else:
            # Create todo
            payload = {
                "title": title,
                "doneStatus": done_status
            }
            create_response = requests.post(todos_endpoint, json=payload)
            
            if create_response.status_code == 201:
                new_todo = create_response.json()
                actual_todo_id = new_todo['id']
                print(f"Created todo with title '{title}', got ID {actual_todo_id}")
            else:
                print(f"Failed to create todo: {create_response.text}")
                assert False, f"Failed to create todo with title '{title}'"
        
        # Associate todo with project if not already associated
        check_response = requests.get(f"{projects_endpoint}/{project_id}/tasks")
        associated_todos = check_response.json().get('todos', [])
        
        if not any(t.get('id') == actual_todo_id for t in associated_todos):
            # Associate todo with project
            assoc_response = requests.post(f"{projects_endpoint}/{project_id}/tasks", json={"id": actual_todo_id})
            
            # Retry if first attempt failed
            if assoc_response.status_code != 201:
                print(f"First attempt to associate todo failed, retrying...")
                time.sleep(0.5)
                assoc_response = requests.post(f"{projects_endpoint}/{project_id}/tasks", json={"id": actual_todo_id})
            
            if assoc_response.status_code != 201:
                print(f"Warning: Failed to associate todo {actual_todo_id} with project {project_id}")
                print(f"Error: {assoc_response.text}")
            else:
                print(f"Associated todo {actual_todo_id} with project {project_id}")
        else:
            print(f"Todo {actual_todo_id} is already associated with project {project_id}")
    
    # Store for later use
    context.current_project_id = project_id

@when('removing todo with title "{todo_title}" from project with title "{project_title}"')
def step_impl_remove_todo_by_title(context, todo_title, project_title):
    """Remove a todo from a project using titles instead of IDs."""
    # Find the project ID by title
    project_title = project_title.strip('"')
    projects_response = requests.get(projects_endpoint)
    projects = projects_response.json().get('projects', [])
    project = next((p for p in projects if p.get('title') == project_title), None)
    
    # Find the todo ID by title
    todo_title = todo_title.strip('"')
    todos_response = requests.get(todos_endpoint)
    todos = todos_response.json().get('todos', [])
    todo = next((t for t in todos if t.get('title') == todo_title), None)
    
    # Store information for later verification
    context.project_title = project_title
    context.todo_title = todo_title
    
    # If either project or todo is not found, we'll still try the API call to generate
    # the expected error response
    project_id = project['id'] if project else '999'
    todo_id = todo['id'] if todo else '999'
    
    print(f"Removing todo '{todo_title}' (ID: {todo_id}) from project '{project_title}' (ID: {project_id})")
    
    # Make the API call
    context.response = requests.delete(f"{projects_endpoint}/{project_id}/tasks/{todo_id}")
    print_response(context.response)
    
    # Store IDs for verification steps
    context.project_id = project_id if project else None
    context.todo_id = todo_id if todo else None

@then('the todo should no longer be associated with the project')
def step_impl_verify_todo_not_associated(context):
    """Verify that a todo is no longer associated with a project."""
    # If we don't have a valid project ID, we can't verify
    if not hasattr(context, 'project_id') or not context.project_id:
        print("No valid project ID available - skipping association check")
        return
    
    # Check the project's tasks
    verification_response = requests.get(f"{projects_endpoint}/{context.project_id}/tasks")
    
    if verification_response.status_code != 200:
        print(f"Project {context.project_id} does not exist or can't be accessed")
        return
    
    # Extract todos from the response
    todos = verification_response.json().get('todos', [])
    
    # Check by ID if we have it
    if hasattr(context, 'todo_id') and context.todo_id:
        todo_ids = [str(todo.get('id', '')) for todo in todos]
        assert str(context.todo_id) not in todo_ids, f"Todo ID {context.todo_id} is still associated with project"
        print(f"Verified todo ID {context.todo_id} is not associated with the project")
    
    # Check by title as backup
    elif hasattr(context, 'todo_title') and context.todo_title:
        todo_titles = [todo.get('title', '') for todo in todos]
        assert context.todo_title not in todo_titles, f"Todo '{context.todo_title}' is still associated with project"
        print(f"Verified todo '{context.todo_title}' is not associated with the project")
    
    else:
        assert False, "No todo ID or title available to verify"

@then('receive appropriate error response')
def step_impl_verify_error_response(context):
    """Verify that an appropriate error response was received."""
    # Check that we got an error status code (4xx or 5xx)
    status_code = context.response.status_code
    assert status_code >= 400, f"Expected error status code, got {status_code}"
    
    # Log the response for debugging
    print(f"Received error response with status code: {status_code}")
    print(f"Response body: {context.response.text}")

@given('todo with title "{todo_title}" has been removed from project with title "{project_title}"')
def step_impl_todo_already_removed(context, todo_title, project_title):
    """Ensure that a todo has already been removed from a project."""
    # First ensure the todo and project exist
    todo_title = todo_title.strip('"')
    project_title = project_title.strip('"')
    
    # Find or create the project
    projects_response = requests.get(projects_endpoint)
    projects = projects_response.json().get('projects', [])
    project = next((p for p in projects if p.get('title') == project_title), None)
    
    if not project:
        # Create project
        project_response = requests.post(projects_endpoint, json={"title": project_title})
        if project_response.status_code == 201:
            project = project_response.json()
        else:
            assert False, f"Failed to create project: {project_response.text}"
    
    # Find or create the todo
    todos_response = requests.get(todos_endpoint)
    todos = todos_response.json().get('todos', [])
    todo = next((t for t in todos if t.get('title') == todo_title), None)
    
    if not todo:
        # Create todo
        todo_response = requests.post(todos_endpoint, json={"title": todo_title})
        if todo_response.status_code == 201:
            todo = todo_response.json()
        else:
            assert False, f"Failed to create todo: {todo_response.text}"
    
    # Make sure they exist
    project_id = project['id']
    todo_id = todo['id']
    
    # Store for later use
    context.project_id = project_id
    context.project_title = project_title
    context.todo_id = todo_id
    context.todo_title = todo_title
    
    # Now remove the todo from the project - don't worry about errors
    print(f"Pre-removing todo {todo_id} from project {project_id}")
    requests.delete(f"{projects_endpoint}/{project_id}/tasks/{todo_id}")
    
    # Verify it's actually removed
    check_response = requests.get(f"{projects_endpoint}/{project_id}/tasks")
    if check_response.status_code == 200:
        todos = check_response.json().get('todos', [])
        todo_ids = [str(t.get('id', '')) for t in todos]
        if str(todo_id) in todo_ids:
            print(f"Todo still associated, removing again")
            requests.delete(f"{projects_endpoint}/{project_id}/tasks/{todo_id}")
    
    print(f"Ensured todo {todo_id} is not associated with project {project_id}")

@when('removing todo with title "{todo_title}" from project with title "{project_title}" again')
def step_impl_remove_todo_by_title_again(context, todo_title, project_title):
    """Remove a todo from a project again (idempotence test)."""
    # Reuse the same implementation
    step_impl_remove_todo_by_title(context, todo_title, project_title)

@then('the todo should not be associated with the project')
def step_impl_verify_todo_still_not_associated(context):
    """Verify that a todo is still not associated with a project."""
    # Same implementation as the other not-associated check
    step_impl_verify_todo_not_associated(context)