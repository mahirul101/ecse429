#!/bin/bash

echo "==== Interoperability Testing: Creating a New Category ===="

curl -X POST 'http://localhost:4567/categories' \
     -H 'Content-Type: application/xml' \
     --data-raw '<category>
                    <title>Assignments</title>
                    <description>All university assignments.</description>
                 </category>' \
     -w "HTTP Status: %{http_code}\n"

echo $'\n================================================================================='

echo "==== Interoperability Testing: Creating a New Project ===="

curl -X POST 'http://localhost:4567/projects' \
     -H 'Content-Type: application/xml' \
     --data-raw '<project>
                    <title>University Work</title>
                    <completed>false</completed>
                    <active>true</active>
                    <description>All tasks related to university.</description>
                 </project>' \
     -w "HTTP Status: %{http_code}\n"

echo $'\n================================================================================='

echo "==== Interoperability Testing: Creating a New Todo ===="

curl -X POST 'http://localhost:4567/todos' \
     -H 'Content-Type: application/xml' \
     --data-raw '<todo>
                    <title>Complete Assignment</title>
                    <doneStatus>false</doneStatus>
                    <description>Finish the REST API interoperability testing.</description>
                 </todo>' \
     -w "HTTP Status: %{http_code}\n"

echo $'\n================================================================================='

echo "==== Interoperability Testing: Creating a Todo-Project Relationship ===="

curl -X POST 'http://localhost:4567/todos/1/tasksof' \
     -H 'Content-Type: application/xml' \
     --data-raw '<project>
                    <id>1</id>
                 </project>' \
     -w "HTTP Status: %{http_code}\n"

echo $'\n================================================================================='

echo "==== Interoperability Testing: Creating a Todo-Category Relationship ===="

curl -X POST 'http://localhost:4567/todos/1/categories' \
     -H 'Content-Type: application/xml' \
     --data-raw '<category>
                    <id>1</id>
                 </category>' \
     -w "HTTP Status: %{http_code}\n"

echo $'\n================================================================================='

# echo "==== Interoperability Testing: Creating a Category-Project Relationship ===="
# curl -X POST 'http://localhost:4567/categories/1/projects' \
#      -H 'Content-Type: application/xml' \
#      --data-raw '<project>
#                     <id>1</id>
#                  </project>' \
#      -w "HTTP Status: %{http_code}\n"

# echo $'\n================================================================================='

echo "==== GET /categories/:id/projects with Nonexistent Category ID ===="
curl -X GET 'http://localhost:4567/categories/20/projects' \
     -H 'Accept: application/xml' \
     -w "HTTP Status: %{http_code}\n"

echo $'\n================================================================================='

echo "==== HEAD /categories/:id/projects with Nonexistent Category ID ===="
curl -I 'http://localhost:4567/categories/20/projects' \
     -H 'Accept: application/xml' \
     -w "HTTP Status: %{http_code}\n"

echo $'\n================================================================================='

echo "==== Interoperability Testing: Retrieving Projects Related to Todo ID = 1 ===="

curl -X GET 'http://localhost:4567/todos/1/tasksof' \
     -H 'Accept: application/xml' \
     -w "HTTP Status: %{http_code}\n"

echo $'\n================================================================================='

echo "==== Interoperability Testing: Retrieving Categories Related to Todo ID = 1 ===="

curl -X GET 'http://localhost:4567/todos/1/categories' \
     -H 'Accept: application/xml' \
     -w "HTTP Status: %{http_code}\n"

echo $'\n================================================================================='

echo "==== Interoperability Testing: Deleting Todo-Project Relationship ===="

curl -X DELETE 'http://localhost:4567/todos/1/tasksof/1' \
     -H 'Accept: application/xml' \
     -w "HTTP Status: %{http_code}\n"

echo $'\n================================================================================='

echo "==== Interoperability Testing: Deleting Todo-Category Relationship ===="

curl -X DELETE 'http://localhost:4567/todos/1/categories/1' \
     -H 'Accept: application/xml' \
     -w "HTTP Status: %{http_code}\n"

echo $'\n================================================================================='

echo "==== GET /categories/:id/todos with Nonexistent Category ID ===="
curl -X GET 'http://localhost:4567/categories/20/todos' \
     -H 'Accept: application/xml' \
     -w "HTTP Status: %{http_code}\n"

echo $'\n================================================================================='

echo "==== HEAD /categories/:id/todos with Nonexistent Category ID ===="
curl -I 'http://localhost:4567/categories/20/todos' \
     -H 'Accept: application/xml' \
     -w "HTTP Status: %{http_code}\n"

echo $'\n================================================================================='

echo "==== POST /categories/:id/projects with Nonexistent Project ID ===="
curl -X POST 'http://localhost:4567/categories/1/projects' \
     -H 'Content-Type: application/xml' \
     --data-raw '<project>
                    <id>20</id>
                 </project>' \
     -w "HTTP Status: %{http_code}\n"

echo $'\n================================================================================='

echo "==== Interoperability Testing: Deleting Todo ID = 1 ===="

curl -X DELETE 'http://localhost:4567/todos/1' \
     -H 'Accept: application/xml' \
     -w "HTTP Status: %{http_code}\n"

echo $'\n================================================================================='

echo "==== Interoperability Testing: Deleting Project ID = 1 ===="

curl -X DELETE 'http://localhost:4567/projects/1' \
     -H 'Accept: application/xml' \
     -w "HTTP Status: %{http_code}\n"

echo $'\n================================================================================='

echo "==== Interoperability Testing: Deleting Category ID = 1 ===="

curl -X DELETE 'http://localhost:4567/categories/1' \
     -H 'Accept: application/xml' \
     -w "HTTP Status: %{http_code}\n"

echo $'\n================================================================================='