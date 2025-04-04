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

# Generate random project data
def generate_random_project():
    return {
        "title": ''.join(random.choices(string.ascii_letters + string.digits, k=10)),
        "description": ''.join(random.choices(string.ascii_letters + string.digits, k=25)),
        "completed": random.choice(["true", "false"]),
    }

# Clear all projects (CAUTION: this deletes everything!)
def clear_all_projects():
    response = requests.get(f"{BASE_URL}/projects")
    print("Clearing all projects...")
    projects = response.json().get('projects', [])
    for project in projects:
        requests.delete(f"{BASE_URL}/projects/{project['id']}")

# Create N random projects
def create_n_projects(n):
    project_ids = []
    for _ in range(n):
        data = generate_random_project()
        response = requests.post(f"{BASE_URL}/projects", json=data)
        if response.status_code in [200, 201]:
            project_ids.append(response.json()['id'])
    return project_ids

# Measure performance for increasing number of objects
def measure_project_performance():
    test_sizes = [1, 5, 10, 50, 200, 400, 600, 800, 1000]
    create_results, update_results, delete_results = [], [], []

    for size in test_sizes:
        print(f"\n=== Testing with {size} pre-existing projects ===")
        clear_all_projects()
        if size > 1:
            base_ids = create_n_projects(size - 1)
        else:
            base_ids = []

        # CREATE
        print("Measuring CREATE...")
        start_cpu = psutil.cpu_percent(interval=0.1)
        start_mem = psutil.virtual_memory().available / (1024 * 1024)
        start_time = time.time()

        new_project = generate_random_project()
        response = requests.post(f"{BASE_URL}/projects", json=new_project)

        end_time = time.time()
        end_cpu = psutil.cpu_percent(interval=0.1)
        end_mem = psutil.virtual_memory().available / (1024 * 1024)

        create_time = (end_time - start_time) * 1000
        cpu_diff = max(0, end_cpu - start_cpu)
        mem_used = start_mem - end_mem
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")

        create_results.append({
            "size": size, "transaction_time": create_time,
            "cpu_usage": cpu_diff, "memory_usage": mem_used,
            "timestamp": timestamp
        })

        print(f"  CREATE: {create_time:.2f} ms, CPU: {cpu_diff:.2f}%, MEM: {mem_used:.2f} MB")

        # Get project ID for update/delete
        if response.status_code in [200, 201]:
            project_id = response.json()['id']

            # UPDATE
            print("Measuring UPDATE...")
            update_payload = {"description": "Updated_" + ''.join(random.choices(string.ascii_letters, k=10))}

            start_cpu = psutil.cpu_percent(interval=0.1)
            start_mem = psutil.virtual_memory().available / (1024 * 1024)
            start_time = time.time()

            response = requests.put(f"{BASE_URL}/projects/{project_id}", json=update_payload)

            end_time = time.time()
            end_cpu = psutil.cpu_percent(interval=0.1)
            end_mem = psutil.virtual_memory().available / (1024 * 1024)

            update_time = (end_time - start_time) * 1000
            cpu_diff = max(0, end_cpu - start_cpu)
            mem_used = start_mem - end_mem

            update_results.append({
                "size": size, "transaction_time": update_time,
                "cpu_usage": cpu_diff, "memory_usage": mem_used,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
            })

            print(f"  UPDATE: {update_time:.2f} ms, CPU: {cpu_diff:.2f}%, MEM: {mem_used:.2f} MB")

            # DELETE
            print("Measuring DELETE...")

            start_cpu = psutil.cpu_percent(interval=0.1)
            start_mem = psutil.virtual_memory().available / (1024 * 1024)
            start_time = time.time()

            response = requests.delete(f"{BASE_URL}/projects/{project_id}")

            end_time = time.time()
            end_cpu = psutil.cpu_percent(interval=0.1)
            end_mem = psutil.virtual_memory().available / (1024 * 1024)

            delete_time = (end_time - start_time) * 1000
            cpu_diff = max(0, end_cpu - start_cpu)
            mem_used = start_mem - end_mem

            delete_results.append({
                "size": size, "transaction_time": delete_time,
                "cpu_usage": cpu_diff, "memory_usage": mem_used,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
            })

            print(f"  DELETE: {delete_time:.2f} ms, CPU: {cpu_diff:.2f}%, MEM: {mem_used:.2f} MB")

    # Optionally save results to JSON
    with open("project_create_results.json", "w") as f:
        json.dump(create_results, f, indent=2)
    with open("project_update_results.json", "w") as f:
        json.dump(update_results, f, indent=2)
    with open("project_delete_results.json", "w") as f:
        json.dump(delete_results, f, indent=2)

    print("\n Results saved to JSON files.")

if __name__ == "__main__":
    measure_project_performance()
