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
def clear_all_todos():
    response = requests.get(f"{BASE_URL}/todos")
    print(f"Clearing all todos...")
    todos = response.json().get('todos', [])
    for todo in todos:
        requests.delete(f"{BASE_URL}/todos/{todo['id']}")

# Function to create a specified number of todos
def create_n_todos(n):
    todo_ids = []
    for _ in range(n):
        todo_data = generate_random_todo()
        response = requests.post(f"{BASE_URL}/todos", json=todo_data)
        if response.status_code == 200 or response.status_code == 201:
            todo_ids.append(response.json()['id'])
    return todo_ids

# Function to measure performance of all operations for each test size
def measure_performance():
    # Expand this list for full testing
    test_sizes = [1, 5, 10, 50, 200, 400, 600, 800, 1000, 2000, 3000, 4000, 5000, 6000, 7000, 8000, 9000, 10000]
    # test_sizes = [1, 5, 10, 50, 200, 400, 600, 800, 1000, 2000]
    create_results = []
    update_results = []
    delete_results = []
    
    # For time series data
    time_series_data = []
    
    for size in test_sizes:
        print(f"\nTesting with {size} pre-existing todos...")
        
        # Clear all existing todos first
        clear_all_todos()
        
        # Create the base set minus 1 (since we'll measure the last creation)
        if size > 1:
            base_todos = create_n_todos(size - 1)
        else:
            base_todos = []
        
        # 1. Measure CREATE performance
        print(f"Measuring CREATE performance...")
        start_cpu = psutil.cpu_percent(interval=0.1)
        start_memory = psutil.virtual_memory().available / (1024 * 1024)  # MB
        start_time = time.time()

        new_todo = generate_random_todo()
        response = requests.post(f"{BASE_URL}/todos", json=new_todo)

        end_time = time.time()
        end_cpu = psutil.cpu_percent(interval=0.1)
        end_memory = psutil.virtual_memory().available / (1024 * 1024)  # MB

        transaction_time = (end_time - start_time) * 1000  # Convert to ms
        cpu_usage = max(0, end_cpu - start_cpu)  # Clamp to zero
        memory_usage = start_memory - end_memory
        
        # Add timestamp for time series data
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
        
        create_results.append({
            "size": size,
            "transaction_time": transaction_time,
            "cpu_usage": cpu_usage,
            "memory_usage": memory_usage,
            "timestamp": timestamp
        })
        
        time_series_data.append({
            "operation": "Create",
            "size": size,
            "transaction_time": transaction_time,
            "cpu_usage": cpu_usage,
            "memory_usage": memory_usage,
            "timestamp": timestamp
        })
        
        print(f"  Create transaction time: {transaction_time:.2f} ms")
        print(f"  Create CPU usage: {cpu_usage:.2f}%")
        print(f"  Create memory usage: {memory_usage:.2f} MB")
        
        # Get the ID of the newly created todo for update and delete operations
        if response.status_code == 200 or response.status_code == 201:
            test_todo_id = response.json()['id']
            
            # 2. Measure UPDATE performance
            print(f"Measuring UPDATE performance...")
            start_cpu = psutil.cpu_percent(interval=0.1)
            start_memory = psutil.virtual_memory().available / (1024 * 1024)  # MB
            start_time = time.time()
            
            updated_todo = generate_random_todo()
            response = requests.put(f"{BASE_URL}/todos/{test_todo_id}", json=updated_todo)
            
            end_time = time.time()
            end_cpu = psutil.cpu_percent(interval=0.1)
            end_memory = psutil.virtual_memory().available / (1024 * 1024)  # MB
            
            transaction_time = (end_time - start_time) * 1000  # Convert to ms
            cpu_usage = max(0, end_cpu - start_cpu)
            memory_usage = start_memory - end_memory
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
            
            update_results.append({
                "size": size,
                "transaction_time": transaction_time,
                "cpu_usage": cpu_usage,
                "memory_usage": memory_usage,
                "timestamp": timestamp
            })
            
            time_series_data.append({
                "operation": "Update",
                "size": size,
                "transaction_time": transaction_time,
                "cpu_usage": cpu_usage,
                "memory_usage": memory_usage,
                "timestamp": timestamp
            })
            
            print(f"  Update transaction time: {transaction_time:.2f} ms")
            print(f"  Update CPU usage: {cpu_usage:.2f}%")
            print(f"  Update memory usage: {memory_usage:.2f} MB")
            
            # 3. Measure DELETE performance
            print(f"Measuring DELETE performance...")
            start_cpu = psutil.cpu_percent(interval=0.1)
            start_memory = psutil.virtual_memory().available / (1024 * 1024)  # MB
            start_time = time.time()
            
            response = requests.delete(f"{BASE_URL}/todos/{test_todo_id}")
            
            end_time = time.time()
            end_cpu = psutil.cpu_percent(interval=0.1)
            end_memory = psutil.virtual_memory().available / (1024 * 1024)  # MB
            
            transaction_time = (end_time - start_time) * 1000  # Convert to ms
            cpu_usage = max(0, end_cpu - start_cpu)
            memory_usage = start_memory - end_memory
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
            
            delete_results.append({
                "size": size,
                "transaction_time": transaction_time,
                "cpu_usage": cpu_usage,
                "memory_usage": memory_usage,
                "timestamp": timestamp
            })
            
            time_series_data.append({
                "operation": "Delete",
                "size": size,
                "transaction_time": transaction_time,
                "cpu_usage": cpu_usage,
                "memory_usage": memory_usage,
                "timestamp": timestamp
            })
            
            print(f"  Delete transaction time: {transaction_time:.2f} ms")
            print(f"  Delete CPU usage: {cpu_usage:.2f}%")
            print(f"  Delete memory usage: {memory_usage:.2f} MB")
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
    # Convert timestamps to datetime objects and compute sample times 
    # Calculate elapsed time in ms for each operation
    start_time = datetime.strptime(time_series_data[0]["timestamp"], "%Y-%m-%d %H:%M:%S.%f")  # Parse the first timestamp
    for item in time_series_data:
        current_time = datetime.strptime(item["timestamp"], "%Y-%m-%d %H:%M:%S.%f")  # Parse the current timestamp
        item["elapsed_time"] = (current_time - start_time).total_seconds() * 1000  # Convert to milliseconds
    
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
    create_results, update_results, delete_results, time_series_data = measure_performance()
    
    # Plot the results
    plot_results(create_results, update_results, delete_results, time_series_data)
    
    print("\nTesting completed. Results saved to plots/todos/ directory.")