import requests
import time
import psutil
import json
import matplotlib.pyplot as plt
import os
import numpy as np
import random
import string
from datetime import datetime

# Base URL for the API
BASE_URL = "http://localhost:4567"

# Function to generate random todo data
def generate_random_todo():
    return {
        "title": ''.join(random.choices(string.ascii_letters + string.digits, k=10)),
        "description": ''.join(random.choices(string.ascii_letters + string.digits, k=20)),
        "doneStatus": random.choice([True, False]),
    }

# Function to clear all todos

def clear_all_todos(session):
    response = session.get(f"{BASE_URL}/todos")
    print(f"Clearing all todos...")
    todos = response.json().get('todos', [])
    for todo in todos:
        session.delete(f"{BASE_URL}/todos/{todo['id']}")
    #print(f"Cleared {len(todos)} todos.")
'''
def clear_all_todos(session):

    response = session.get(f"{BASE_URL}/todos")
    print(f"Clearing all todos...")
    todos = response.json().get('todos', [])
    total = len(todos)
    print(f"Found {total} todos to clear.")
    
    batch_size = 100
    for i in range(0, total, batch_size):
        batch = todos[i:i+batch_size]
        for todo in batch:
            try:
                session.delete(f"{BASE_URL}/todos/{todo['id']}")
            except Exception as e:
                print(f"Error deleting todo {todo['id']}: {e}")
                time.sleep(0.1)

        print(f"Cleared {min(i+batch_size, total)}/{total} todos...")
        time.sleep(0.5)
    
    print(f"Cleared {total} todos.")
'''
# Function to create a specified number of todos
def create_n_todos(n, session):
    todo_ids = []
    for _ in range(n):
        todo_data = generate_random_todo()
        response = session.post(f"{BASE_URL}/todos", json=todo_data)
        if response.status_code == 200 or response.status_code == 201:
            todo_ids.append(response.json()['id'])
    return todo_ids

# Improved measurement function for single operations
def measure_operation(operation_func, *args):
    # Process-specific measurements
    process = psutil.Process(os.getpid())
    
    # Take baseline measurements
    start_memory = psutil.virtual_memory().available / (1024 * 1024)  # MB
    
    # Measure initial CPU to establish baseline
    process.cpu_percent()  # First call initializes monitoring but returns meaningless value
    time.sleep(0.1)  # Short delay to let CPU monitoring stabilize
    
    start_time = time.time()
    
    # Perform the operation
    result = operation_func(*args)
    
    # Take end measurements
    end_time = time.time()
    cpu_usage = process.cpu_percent()  # Get CPU usage since last call
    end_memory = psutil.virtual_memory().available / (1024 * 1024)  # MB
    
    # Calculate metrics
    transaction_time = (end_time - start_time) * 1000  # Convert to ms
    memory_delta = abs(end_memory - start_memory)  # Use absolute value
    
    return result, {
        "transaction_time": transaction_time,
        "cpu_usage": cpu_usage,
        "memory_usage": memory_delta,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
    }

# Function to measure performance of all operations for each test size
def measure_performance(session):
    # Expand this list for full testing
    test_sizes = [1, 5, 10, 50, 75, 100, 200, 300, 400, 500, 600, 700, 800, 900, 1000, 2000, 3000, 4000, 5000, 6000, 7000, 8000, 9000, 10000]
    # test_sizes = [1, 5, 10, 50, 200, 400, 600, 800, 1000, 2000]
    create_results = []
    update_results = []
    delete_results = []

    # For time series data
    time_series_data = []

    for size in test_sizes:
        print(f"\nTesting with {size} pre-existing todos...")

        # Clear all existing todos first
        clear_all_todos(session)
        time.sleep(0.5)  # Give the server a moment to clear

        # Create the base set minus 1 (since we'll measure the last creation)
        if size > 1:
            base_todos = create_n_todos(size - 1, session)
        else:
            base_todos = []

        # Short pause to let system stabilize
        time.sleep(0.5)

        # 1. Measure CREATE performance
        print(f"Measuring CREATE performance...")
        new_todo = generate_random_todo()
        
        def create_operation():
            return session.post(f"{BASE_URL}/todos", json=new_todo)
        
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

        # Get the ID of the newly created todo for update and delete operations
        if response.status_code == 200 or response.status_code == 201:
            test_todo_id = response.json()['id']

            # Short pause between operations
            time.sleep(0.2)
            
            # 2. Measure UPDATE performance
            print(f"Measuring UPDATE performance...")
            updated_todo = generate_random_todo()
            
            def update_operation():
                return session.put(f"{BASE_URL}/todos/{test_todo_id}", json=updated_todo)
            
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

            # Short pause between operations
            time.sleep(0.2)
            
            # 3. Measure DELETE performance
            print(f"Measuring DELETE performance...")
            
            def delete_operation():
                return session.delete(f"{BASE_URL}/todos/{test_todo_id}")
            
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
            print(f"Error creating test todo: {response.status_code}")

    return create_results, update_results, delete_results, time_series_data

# Function to plot the results
def plot_results(create_results, update_results, delete_results, time_series_data):
    # Create directories for plots
    os.makedirs("plots/todos", exist_ok=True)
    
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
    plt.xscale('log')
    plt.xlabel('Number of Todos')
    plt.ylabel('Transaction Time (ms)')
    plt.title('Transaction Time vs. Number of Todos')
    plt.legend()
    plt.grid(True)
    plt.savefig('plots/todos/transaction_time_vs_objects.png')
    
    # Plot CPU usage vs. number of objects
    plt.figure(figsize=(12, 6))
    plt.plot(sizes, create_cpu, 'o-', label='Create')
    plt.plot(sizes, update_cpu, 's-', label='Update')
    plt.plot(sizes, delete_cpu, '^-', label='Delete')
    plt.xscale('log')
    plt.xlabel('Number of Todos')
    plt.ylabel('CPU Usage (%)')
    plt.title('CPU Usage vs. Number of Todos')
    plt.legend()
    plt.grid(True)
    plt.savefig('plots/todos/cpu_usage_vs_objects.png')
    
    # Plot memory usage vs. number of objects
    plt.figure(figsize=(12, 6))
    plt.plot(sizes, create_memory, 'o-', label='Create')
    plt.plot(sizes, update_memory, 's-', label='Update')
    plt.plot(sizes, delete_memory, '^-', label='Delete')
    plt.xscale('log')
    plt.xlabel('Number of Todos')
    plt.ylabel('Memory Usage (MB)')
    plt.title('Memory Usage vs. Number of Todos')
    plt.legend()
    plt.grid(True)
    plt.savefig('plots/todos/memory_usage_vs_objects.png')
    
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

    plt.xlabel('Elapsed Time (ms)')
    plt.ylabel('Transaction Time (ms)')
    plt.title('Transaction Time vs Elapsed Time')
    plt.legend()
    plt.grid(True)
    plt.savefig('plots/todos/transaction_time_vs_elapsed_time.png')

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

    plt.xlabel('Elapsed Time (ms)')
    plt.ylabel('CPU Usage (%)')
    plt.title('CPU Usage vs Elapsed Time')
    plt.legend()
    plt.grid(True)
    plt.savefig('plots/todos/cpu_usage_vs_elapsed_time.png')

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

    plt.xlabel('Elapsed Time (ms)')
    plt.ylabel('Memory Usage (MB)')
    plt.title('Memory Usage vs Elapsed Time')
    plt.legend()
    plt.grid(True)
    plt.savefig('plots/todos/memory_usage_vs_elapsed_time.png')

    # Save results to file
    all_results = {
        "create": create_results,
        "update": update_results,
        "delete": delete_results,
        "time_series": time_series_data
    }

    os.makedirs("results", exist_ok=True)
    with open("results/todos_results.json", "w") as f:
        json.dump(all_results, f, indent=2, default=str)

if __name__ == "__main__":
    # Run the optimized tests
    print("Starting performance measurements...")
    session = requests.Session()
    create_results, update_results, delete_results, time_series_data = measure_performance(session)

    # Plot the results
    plot_results(create_results, update_results, delete_results, time_series_data)

    print("\nTesting completed. Results saved to plots/todos/ directory.")