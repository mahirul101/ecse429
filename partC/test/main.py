import os
import sys
import subprocess
import argparse

def run_test(test_file):
    """Run a specific test file."""
    print(f"Running test: {test_file}")
    subprocess.run([sys.executable, test_file])

def main():
    """Main function to run the performance tests."""
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description='Run API performance tests')
    parser.add_argument('--all', action='store_true', help='Run all tests')
    parser.add_argument('--todos', action='store_true', help='Run tests for todos')
    parser.add_argument('--projects', action='store_true', help='Run tests for projects')
    parser.add_argument('--categories', action='store_true', help='Run tests for categories')
    parser.add_argument('--relationships', action='store_true', help='Run tests for relationships')

    args = parser.parse_args()

    # If no specific test is selected, run all tests
    if not (args.todos or args.projects or args.categories or args.relationships):
        args.all = True

    # Create directories for results and plots
    os.makedirs("results", exist_ok=True)
    os.makedirs("plots", exist_ok=True)

    # Run selected tests
    if args.all or args.todos:
        run_test("test_todo.py")
    
    if args.all or args.projects:
        run_test("test_project.py")

    if args.all or args.categories:
        run_test("test_category.py")

if __name__ == "__main__":
    main()
