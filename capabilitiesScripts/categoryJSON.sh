#!/bin/bash

echo "==== Fetching All Categories ===="

curl -X GET 'http://localhost:4567/categories' \
     -H 'Accept: application/json' \
     -w "HTTP Status: %{http_code}\n"

echo $'\n================================================================================='

echo "==== Sending HEAD Request to /categories ===="

curl -I 'http://localhost:4567/categories' \
     -H 'Accept: application/json' \
     -w "HTTP Status: %{http_code}\n"

echo $'\n================================================================================='

echo "==== Creating a New Category (POST to /categories) ===="

curl -X POST 'http://localhost:4567/categories' \
     -H 'Accept: application/json' \
     -H 'Content-Type: application/json' \
     --data-raw '{
                    "description": "University work",
                    "title": "University"
                 }' \
     -w "HTTP Status: %{http_code}\n"

echo $'\n================================================================================='

echo "==== Fetching Category with ID 1 ===="

curl -X GET 'http://localhost:4567/categories/1' \
     -H 'Accept: application/json' \
     -w "HTTP Status: %{http_code}\n"

echo $'\n================================================================================='

echo "==== Fetching Non-Existent Category (ID 20) ===="

curl -X GET 'http://localhost:4567/categories/20' \
     -H 'Accept: application/json' \
     -w "HTTP Status: %{http_code}\n"

echo $'\n================================================================================='

echo "==== HEAD Request for Category with ID 1 ===="

curl -I 'http://localhost:4567/categories/1' \
     -H 'Accept: application/json' \
     -w "HTTP Status: %{http_code}\n"

echo $'\n================================================================================='

echo "==== HEAD Request for Non-Existent Category (ID 20) ===="

curl -I 'http://localhost:4567/categories/20' \
     -H 'Accept: application/json' \
     -w "HTTP Status: %{http_code}\n"

echo $'\n================================================================================='

echo "==== Deleting Category with ID 2 ===="

curl -X DELETE 'http://localhost:4567/categories/2' \
     -H 'Accept: application/json' \
     -w "HTTP Status: %{http_code}\n"

echo $'\n================================================================================='

echo "==== Attempting to Delete Non-Existent Category (ID 20) ===="

curl -X DELETE 'http://localhost:4567/categories/20' \
     -H 'Accept: application/json' \
     -w "HTTP Status: %{http_code}\n"

echo $'\n================================================================================='

echo "==== Updating Category (POST to /categories/3) ===="

curl -X POST 'http://localhost:4567/categories/3' \
     -H 'Accept: application/json' \
     -H 'Content-Type: application/json' \
     --data-raw '{
                    "title": "COMP360 Assignment"
                 }' \
     -w "HTTP Status: %{http_code}\n"

echo $'\n================================================================================='

echo "==== Full Update (PUT to /categories/3) ===="

curl -X PUT 'http://localhost:4567/categories/3' \
     -H 'Accept: application/json' \
     -H 'Content-Type: application/json' \
     --data-raw '{
                    "description": "Verify answers",
                    "title": "COMP360"
                 }' \
     -w "HTTP Status: %{http_code}\n"

echo $'\n================================================================================='

echo "==== PUT Request with Non-Existent Category ID (20) ===="

curl -X PUT 'http://localhost:4567/categories/20' \
     -H 'Accept: application/json' \
     -H 'Content-Type: application/json' \
     --data-raw '{
                    "description": "Check responses",
                    "title": "COMP360"
                 }' \
     -w "HTTP Status: %{http_code}\n"

echo $'\n================================================================================='

echo "==== Creating Category-Project Relationship (POST to /categories/1/projects) ===="

curl -X POST 'http://localhost:4567/categories/1/projects' \
     -H 'Content-Type: application/json' \
     --data-raw '{"id": "1"}' \
     -w "HTTP Status: %{http_code}\n"

echo $'\n================================================================================='

echo "==== Fetching Category-Project Relationship (GET /categories/1/projects) ===="

curl -X GET 'http://localhost:4567/categories/1/projects' \
     -H 'Accept: application/json' \
     -w "HTTP Status: %{http_code}\n"

echo $'\n================================================================================='

echo "==== Attempting to Fetch Project Relationship for Invalid Category (ID 20) ===="

curl -X GET 'http://localhost:4567/categories/20/projects' \
     -H 'Accept: application/json' \
     -w "HTTP Status: %{http_code}\n"

echo $'\n================================================================================='

echo "==== HEAD Request for Existing Category-Todo Relationship ===="

curl -I 'http://localhost:4567/categories/1/todos' \
     -H 'Accept: application/json' \
     -w "HTTP Status: %{http_code}\n"

echo $'\n================================================================================='

echo "==== GET Request for Non-Existent Category-Todo Relationship ===="

curl -X GET 'http://localhost:4567/categories/20/todos' \
     -H 'Accept: application/json' \
     -w "HTTP Status: %{http_code}\n"

echo $'\n================================================================================='

echo "==== POST to Create Category-Todo Relationship ===="

curl -X POST 'http://localhost:4567/categories/1/todos' \
     -H 'Content-Type: application/json' \
     --data-raw '{"id": "1"}' \
     -w "HTTP Status: %{http_code}\n"

echo $'\n================================================================================='

echo "==== DELETE Existing Category-Todo Relationship (ID 1) ===="

curl -X DELETE 'http://localhost:4567/categories/1/todos/1' \
     -H 'Accept: application/json' \
     -w "HTTP Status: %{http_code}\n"

echo $'\n================================================================================='