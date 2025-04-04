import requests
import time
import psutil
import json
import matplotlib.pyplot as plt
import os
import random
import string
from datetime import datetime

# Base URL for the API
BASE_URL = "http://localhost:4567"

# Generate random category data
def generate_random_category():
    return {
        "title": ''.join(random.choices(string.ascii_letters + string.digits, k=10)),
        "description": ''.join(random.choices(string.ascii_letters + string.digits, k=25)),
    }

# Clear all categories
def clear_all_categories(session):
    response = session.get(f"{BASE_URL}/categories")
    print("Clearing all categories...")
    categories = response.json().get('categories', [])
    for category in categories:
        session.delete(f"{BASE_URL}/categories/{category['id']}")

# Create N random categories
def create_n_categories(n, session):
    category_ids = []
    for _ in range(n):
        data = generate_random_category()
        response = session.post(f"{BASE_URL}/categories", json=data)
        if response.status_code in [200, 201]:
            category_ids.append(response.json()['id'])
    return category_ids

# Improved measurement function for single operations
def measure_operation(operation_func, *args):
    # Process-specific measurements
    process = psutil.Process(os.getpid())
    
    # Take baseline measurements
    start_memory = process.memory_info().rss / (1024 * 1024)  # MB
    
    # Measure initial CPU to establish baseline
    process.cpu_percent()  # First call initializes monitoring but returns meaningless value
    time.sleep(0.1)  # Short delay to let CPU monitoring stabilize
    
    start_time = time.time()
    
    # Perform the operation
    result = operation_func(*args)
    
    # Take end measurements
    end_time = time.time()
    cpu_usage = process.cpu_percent()  # Get CPU usage since last call
    end_memory = process.memory_info().rss / (1024 * 1024)  # MB
    
    # Calculate metrics
    transaction_time = (end_time - start_time) * 1000  # Convert to ms
    memory_delta = abs(end_memory - start_memory)  # Use absolute value
    
    return result, {
        "transaction_time": transaction_time,
        "cpu_usage": cpu_usage,
        "memory_usage": memory_delta,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
    }

# Measure performance for increasing number of objects
def measure_category_performance(session):
    test_sizes = [1, 5, 10, 50, 75, 100, 200, 300, 400, 500, 600, 700, 800, 900, 1000, 2000, 3000, 4000, 5000, 6000, 7000, 8000, 9000, 10000]
    create_results = []
    update_results = []
    delete_results = []
    #relationship_results = []  # For relationship operations
    time_series_data = []

    for size in test_sizes:
        print(f"\n=== Testing with {size} pre-existing categories ===")
        
        # Clear all existing categories first
        clear_all_categories(session)
        time.sleep(0.5)  # Give the server a moment to clear
        
        # Create the base set minus 1 (since we'll measure the last creation)
        if size > 1:
            base_categories = create_n_categories(size - 1,session)
        else:
            base_categories = []

        # Short pause to let system stabilize
        time.sleep(0.5)

        # 1. Measure CREATE performance
        print("Measuring CREATE performance...")
        new_category = generate_random_category()
        
        def create_operation():
            return session.post(f"{BASE_URL}/categories", json=new_category)
        
        response, create_metrics = measure_operation(create_operation)
        create_metrics["size"] = size
        create_results.append(create_metrics)
        
        time_series_data.append({
            "operation": "Create",
            "size": size,
            **create_metrics
        })

        print(f"  Create transaction time: {create_metrics['transaction_time']:.2f} ms")
        print(f"  Create CPU usage: {create_metrics['cpu_usage']:.2f}%")
        print(f"  Create memory usage: {create_metrics['memory_usage']:.2f} MB")

        # Get the ID of the newly created category for update and delete operations
        if response.status_code in [200, 201]:
            category_id = response.json()['id']

            # Short pause between operations
            time.sleep(0.2)
            
            # 2. Measure UPDATE performance
            print("Measuring UPDATE performance...")
            update_payload = {"description": "Updated_" + ''.join(random.choices(string.ascii_letters, k=10))}
            
            def update_operation():
                return session.put(f"{BASE_URL}/categories/{category_id}", json=update_payload)
            
            response, update_metrics = measure_operation(update_operation)
            update_metrics["size"] = size
            update_results.append(update_metrics)
            
            time_series_data.append({
                "operation": "Update",
                "size": size,
                **update_metrics
            })

            print(f"  Update transaction time: {update_metrics['transaction_time']:.2f} ms")
            print(f"  Update CPU usage: {update_metrics['cpu_usage']:.2f}%")
            print(f"  Update memory usage: {update_metrics['memory_usage']:.2f} MB")

            # 3. Measure relationship operations (if a project exists)
            # Create a test project to relate to the category
            test_project = {
                "title": ''.join(random.choices(string.ascii_letters + string.digits, k=10)),
                "description": ''.join(random.choices(string.ascii_letters + string.digits, k=25)),
                "completed": random.choice([True, False]),
            }
            project_response = session.post(f"{BASE_URL}/projects", json=test_project)
            
            if project_response.status_code in [200, 201]:
                project_id = project_response.json()['id']
                
                # Measure creating a relationship
                #print("Measuring RELATIONSHIP CREATE performance...")
                
                #def relationship_operation():
                #    return session.post(f"{BASE_URL}/categories/{category_id}/projects", json={"id": project_id})
                
                #response, relationship_metrics = measure_operation(relationship_operation)
                #relationship_metrics["size"] = size
                #relationship_results.append(relationship_metrics)
                
                #time_series_data.append({
                #    "operation": "Relationship",
                #    "size": size,
                #    **relationship_metrics
                #})

                #print(f"  Relationship transaction time: {relationship_metrics['transaction_time']:.2f} ms")
                #print(f"  Relationship CPU usage: {relationship_metrics['cpu_usage']:.2f}%")
                #print(f"  Relationship memory usage: {relationship_metrics['memory_usage']:.2f} MB")
                
                # Clean up the relationship
                session.delete(f"{BASE_URL}/categories/{category_id}/projects/{project_id}")
                # Clean up the test project
                session.delete(f"{BASE_URL}/projects/{project_id}")

            # Short pause between operations
            time.sleep(0.2)
            
            # 4. Measure DELETE performance
            print("Measuring DELETE performance...")
            
            def delete_operation():
                return session.delete(f"{BASE_URL}/categories/{category_id}")
            
            response, delete_metrics = measure_operation(delete_operation)
            delete_metrics["size"] = size
            delete_results.append(delete_metrics)
            
            time_series_data.append({
                "operation": "Delete",
                "size": size,
                **delete_metrics
            })

            print(f"  Delete transaction time: {delete_metrics['transaction_time']:.2f} ms")
            print(f"  Delete CPU usage: {delete_metrics['cpu_usage']:.2f}%")
            print(f"  Delete memory usage: {delete_metrics['memory_usage']:.2f} MB")
        else:
            print(f"Error creating test category: {response.status_code}")

    return create_results, update_results, delete_results, time_series_data

# Function to plot the results
def plot_results(create_results, update_results, delete_results, time_series_data):
    # Create directories for plots
    os.makedirs("plots/categories", exist_ok=True)
    
    # 1. Plots vs. Number of Objects
    # Extract data from results
    sizes = [r["size"] for r in create_results]
    create_times = [r["transaction_time"] for r in create_results]
    update_times = [r["transaction_time"] for r in update_results]
    delete_times = [r["transaction_time"] for r in delete_results]
    
    create_cpu = [r["cpu_usage"] for r in create_results]
    update_cpu = [r["cpu_usage"] for r in update_results]
    delete_cpu = [r["cpu_usage"] for r in delete_results]
    
    create_memory = [r["memory_usage"] for r in create_results]
    update_memory = [r["memory_usage"] for r in update_results]
    delete_memory = [r["memory_usage"] for r in delete_results]
    
    # Plot transaction time vs. number of objects
    plt.figure(figsize=(12, 6))
    plt.plot(sizes, create_times, 'o-', label='Create')
    plt.plot(sizes, update_times, 's-', label='Update')
    plt.plot(sizes, delete_times, '^-', label='Delete')
    #if relationship_results:
    #    relationship_times = [r["transaction_time"] for r in relationship_results]
    #    plt.plot(sizes[:len(relationship_results)], relationship_times, 'x-', label='Relationship')
    plt.xscale('log')
    plt.xlabel('Number of Categories')
    plt.ylabel('Transaction Time (ms)')
    plt.title('Transaction Time vs. Number of Categories')
    plt.legend()
    plt.grid(True)
    plt.savefig('plots/categories/transaction_time_vs_objects.png')
    
    # Plot CPU usage vs. number of objects
    plt.figure(figsize=(12, 6))
    plt.plot(sizes, create_cpu, 'o-', label='Create')
    plt.plot(sizes, update_cpu, 's-', label='Update')
    plt.plot(sizes, delete_cpu, '^-', label='Delete')
   #if relationship_results:
   #    relationship_cpu = [r["cpu_usage"] for r in relationship_results]
   #    plt.plot(sizes[:len(relationship_results)], relationship_cpu, 'x-', label='Relationship')
    plt.xscale('log')
    plt.xlabel('Number of Categories')
    plt.ylabel('CPU Usage (%)')
    plt.title('CPU Usage vs. Number of Categories')
    plt.legend()
    plt.grid(True)
    plt.savefig('plots/categories/cpu_usage_vs_objects.png')
    
    # Plot memory usage vs. number of objects
    plt.figure(figsize=(12, 6))
    plt.plot(sizes, create_memory, 'o-', label='Create')
    plt.plot(sizes, update_memory, 's-', label='Update')
    plt.plot(sizes, delete_memory, '^-', label='Delete')
    #if relationship_results:
    #    relationship_memory = [r["memory_usage"] for r in relationship_results]
    #    plt.plot(sizes[:len(relationship_results)], relationship_memory, 'x-', label='Relationship')
    plt.xscale('log')
    plt.xlabel('Number of Categories')
    plt.ylabel('Memory Usage (MB)')
    plt.title('Memory Usage vs. Number of Categories')
    plt.legend()
    plt.grid(True)
    plt.savefig('plots/categories/memory_usage_vs_objects.png')
    
    # 2. Time Series Plots
    # Calculate elapsed time in ms for each operation
    start_time = datetime.strptime(time_series_data[0]["timestamp"], "%Y-%m-%d %H:%M:%S.%f")
    for item in time_series_data:
        current_time = datetime.strptime(item["timestamp"], "%Y-%m-%d %H:%M:%S.%f")
        item["elapsed_time"] = (current_time - start_time).total_seconds() * 1000
    
    # Separate data by operation type
    create_data = [d for d in time_series_data if d["operation"] == "Create"]
    update_data = [d for d in time_series_data if d["operation"] == "Update"]
    delete_data = [d for d in time_series_data if d["operation"] == "Delete"]
    #relationship_data = [d for d in time_series_data if d["operation"] == "Relationship"]
    
    # Transaction Time vs Sample Time (for each operation)
    plt.figure(figsize=(12, 6))

    if create_data:
        plt.plot([d["elapsed_time"] for d in create_data], 
                [d["transaction_time"] for d in create_data], 
                'o-', label='Create', color='blue')

    if update_data:
        plt.plot([d["elapsed_time"] for d in update_data], 
                [d["transaction_time"] for d in update_data], 
                's-', label='Update', color='green')

    if delete_data:
        plt.plot([d["elapsed_time"] for d in delete_data], 
                [d["transaction_time"] for d in delete_data], 
                '^-', label='Delete', color='red')
                
    #if relationship_data:
    #    plt.plot([d["elapsed_time"] for d in relationship_data], 
    #            [d["transaction_time"] for d in relationship_data], 
    #            'x-', label='Relationship', color='purple')

    plt.xlabel('Elapsed Time (ms)')
    plt.ylabel('Transaction Time (ms)')
    plt.title('Transaction Time vs Elapsed Time')
    plt.legend()
    plt.grid(True)
    plt.savefig('plots/categories/transaction_time_vs_elapsed_time.png')

    # CPU Usage vs Elapsed Time
    plt.figure(figsize=(12, 6))

    if create_data:
        plt.plot([d["elapsed_time"] for d in create_data], 
                [d["cpu_usage"] for d in create_data], 
                'o-', label='Create', color='blue')

    if update_data:
        plt.plot([d["elapsed_time"] for d in update_data], 
                [d["cpu_usage"] for d in update_data], 
                's-', label='Update', color='green')

    if delete_data:
        plt.plot([d["elapsed_time"] for d in delete_data], 
                [d["cpu_usage"] for d in delete_data], 
                '^-', label='Delete', color='red')
                
    #if relationship_data:
    #    plt.plot([d["elapsed_time"] for d in relationship_data], 
    #            [d["cpu_usage"] for d in relationship_data], 
    #            'x-', label='Relationship', color='purple')

    plt.xlabel('Elapsed Time (ms)')
    plt.ylabel('CPU Usage (%)')
    plt.title('CPU Usage vs Elapsed Time')
    plt.legend()
    plt.grid(True)
    plt.savefig('plots/categories/cpu_usage_vs_elapsed_time.png')

    # Memory Usage vs Elapsed Time
    plt.figure(figsize=(12, 6))

    if create_data:
        plt.plot([d["elapsed_time"] for d in create_data],
                [d["memory_usage"] for d in create_data],
                'o-', label='Create', color='blue')

    if update_data:
        plt.plot([d["elapsed_time"] for d in update_data],
                [d["memory_usage"] for d in update_data],
                's-', label='Update', color='green')

    if delete_data:
        plt.plot([d["elapsed_time"] for d in delete_data],
                [d["memory_usage"] for d in delete_data],
                '^-', label='Delete', color='red')
                
    #if relationship_data:
    #    plt.plot([d["elapsed_time"] for d in relationship_data],
    #            [d["memory_usage"] for d in relationship_data],
    #            'x-', label='Relationship', color='purple')

    plt.xlabel('Elapsed Time (ms)')
    plt.ylabel('Memory Usage (MB)')
    plt.title('Memory Usage vs Elapsed Time')
    plt.legend()
    plt.grid(True)
    plt.savefig('plots/categories/memory_usage_vs_elapsed_time.png')

    # Save results to file
    all_results = {
        "create": create_results,
        "update": update_results,
        "delete": delete_results,
        "time_series": time_series_data
    }

    os.makedirs("results", exist_ok=True)
    with open("results/categories_results.json", "w") as f:
        json.dump(all_results, f, indent=2, default=str)

# Bonus: Test relationship management with todos and projects
def test_relationship_operations(session):
#    print("\n=== Testing Relationship Operations ===")
    
    # Create a test category
    category_data = generate_random_category()
    category_response = session.post(f"{BASE_URL}/categories", json=category_data)
    
    if category_response.status_code not in [200, 201]:
        print("Failed to create test category")
        return
        
    category_id = category_response.json()['id']
    print(f"Created test category with ID: {category_id}")
    
    # Create a test project
    project_data = {
        "title": ''.join(random.choices(string.ascii_letters + string.digits, k=10)),
        "description": ''.join(random.choices(string.ascii_letters + string.digits, k=25)),
        "completed": False
    }
    project_response = session.post(f"{BASE_URL}/projects", json=project_data)
    
    if project_response.status_code not in [200, 201]:
        print("Failed to create test project")
        session.delete(f"{BASE_URL}/categories/{category_id}")
        return
        
    project_id = project_response.json()['id']
    print(f"Created test project with ID: {project_id}")
    
    # Create a test todo
    todo_data = {
        "title": ''.join(random.choices(string.ascii_letters + string.digits, k=10)),
        "description": ''.join(random.choices(string.ascii_letters + string.digits, k=25)),
        "doneStatus": False
    }
    todo_response = session.post(f"{BASE_URL}/todos", json=todo_data)
    
    if todo_response.status_code not in [200, 201]:
        print("Failed to create test todo")
        session.delete(f"{BASE_URL}/projects/{project_id}")
        session.delete(f"{BASE_URL}/categories/{category_id}")
        return
        
    todo_id = todo_response.json()['id']
    print(f"Created test todo with ID: {todo_id}")
    
    # Test relationships
    results = []
    
    # 1. Add project to category
    print("\nTesting: Add project to category")
    def add_project_to_category():
        return session.post(f"{BASE_URL}/categories/{category_id}/projects", json={"id": project_id})
        
    response, metrics = measure_operation(add_project_to_category)
    print(f"  Status: {response.status_code}")
    print(f"  Transaction time: {metrics['transaction_time']:.2f} ms")
    results.append({"operation": "Add project to category", "metrics": metrics})
    
    # 2. Get projects for category
    print("\nTesting: Get projects for category")
    def get_category_projects():
        return session.get(f"{BASE_URL}/categories/{category_id}/projects")
        
    response, metrics = measure_operation(get_category_projects)
    print(f"  Status: {response.status_code}")
    print(f"  Transaction time: {metrics['transaction_time']:.2f} ms")
    if response.status_code == 200:
        projects = response.json().get('projects', [])
        print(f"  Projects found: {len(projects)}")
    results.append({"operation": "Get projects for category", "metrics": metrics})
    
    # 3. Add todo to category
    print("\nTesting: Add todo to category")
    def add_todo_to_category():
        return session.post(f"{BASE_URL}/categories/{category_id}/todos", json={"id": todo_id})
        
    response, metrics = measure_operation(add_todo_to_category)
    print(f"  Status: {response.status_code}")
    print(f"  Transaction time: {metrics['transaction_time']:.2f} ms")
    results.append({"operation": "Add todo to category", "metrics": metrics})
    
    # 4. Get todos for category
    print("\nTesting: Get todos for category")
    def get_category_todos():
        return session.get(f"{BASE_URL}/categories/{category_id}/todos")
        
    response, metrics = measure_operation(get_category_todos)
    print(f"  Status: {response.status_code}")
    print(f"  Transaction time: {metrics['transaction_time']:.2f} ms")
    if response.status_code == 200:
        todos = response.json().get('todos', [])
        print(f"  Todos found: {len(todos)}")
    results.append({"operation": "Get todos for category", "metrics": metrics})
    
    # 5. Delete project relationship
    print("\nTesting: Delete project relationship")
    def delete_project_relationship():
        return session.delete(f"{BASE_URL}/categories/{category_id}/projects/{project_id}")
        
    response, metrics = measure_operation(delete_project_relationship)
    print(f"  Status: {response.status_code}")
    print(f"  Transaction time: {metrics['transaction_time']:.2f} ms")
    results.append({"operation": "Delete project relationship", "metrics": metrics})
    
    # 6. Delete todo relationship
    print("\nTesting: Delete todo relationship")
    def delete_todo_relationship():
        return session.delete(f"{BASE_URL}/categories/{category_id}/todos/{todo_id}")
        
    response, metrics = measure_operation(delete_todo_relationship)
    print(f"  Status: {response.status_code}")
    print(f"  Transaction time: {metrics['transaction_time']:.2f} ms")
    results.append({"operation": "Delete todo relationship", "metrics": metrics})
    
    # Clean up
    session.delete(f"{BASE_URL}/todos/{todo_id}")
    session.delete(f"{BASE_URL}/projects/{project_id}")
    session.delete(f"{BASE_URL}/categories/{category_id}")
    
    # Save results
    os.makedirs("results", exist_ok=True)
    with open("results/category_relationships_results.json", "w") as f:
        json.dump(results, f, indent=2, default=str)
    
    print("\nRelationship testing completed. Results saved to results/category_relationships_results.json")
    
    return results

if __name__ == "__main__":
    # Run the optimized tests
    print("Starting performance measurements for categories...")
    session = requests.Session()
    create_results, update_results, delete_results, time_series_data = measure_category_performance(session)

    # Plot the results
    plot_results(create_results, update_results, delete_results, time_series_data)
    
    # Test relationship operations
    #relationship_detailed_results = test_relationship_operations(session)

    print("\nTesting completed. Results saved to plots/categories/ directory.")