echo "==== Fetching All Projects ===="

curl -X GET "http://localhost:4567/projects" \
     -H "Accept: application/json" \
     -w "\nHTTP Status: %{http_code}\n"


# Head request for projects

echo $'\n================================================================================='

echo "==== Sending HEAD Request to /projects ===="
curl -I "http://localhost:4567/projects" \
     -H "Accept: application/json" \
     -w "\nHTTP Status: %{http_code}\n"

echo $'\n================================================================================='

echo "==== Creating a New Project (POST to /projects) with title and description ==== "
curl -X POST "http://localhost:4567/projects" \
     -H "Accept: application/json" \
     -H "Content-Type: application/json" \
     --data-raw '{
                    "description": "University work",
                    "title": "University"
                 }' \
     -w "\nHTTP Status: %{http_code}\n"

echo $'\n================================================================================='

echo "==== Fetching Project with ID 1 ===="

curl -X GET "http://localhost:4567/projects/1" \
     -H "Accept: application/json" \
     -w "\nHTTP Status: %{http_code}\n"

echo $'\n================================================================================='


echo "==== Head Request for Project with ID 1 ===="

curl -I "http://localhost:4567/projects/1" \
     -H "Accept: application/json" \
     -w "\nHTTP Status: %{http_code}\n"

echo $'\n================================================================================='

echo "==== Fetching Non-Existent Project (ID 20) ===="
curl -X GET "http://localhost:4567/projects/20" \
     -H "Accept: application/json" \
     -w "\nHTTP Status: %{http_code}\n"

echo $'\n================================================================================='

echo "==== Delete existing project with ID 1 ===="

curl -X DELETE "http://localhost:4567/projects/1" \
     -H "Accept: application/json" \
     -w "\nHTTP Status: %{http_code}\n"
echo $'\n================================================================================='

echo "==== Delete non existing project with ID 20 ===="

curl -X DELETE "http://localhost:4567/projects/20" \
     -H "Accept: application/json" \
     -w "\nHTTP Status: %{http_code}\n"

echo $'\n================================================================================='

echo "==== Delte project with no ID ===="

curl -X DELETE "http://localhost:4567/projects" \
     -H "Accept: application/json" \
     -w "\nHTTP Status: %{http_code}\n"

echo $'\n================================================================================='

# Get existing proect todo relaitonship
echo "==== Fetching Todos for Project with ID 1 ===="
curl -X GET "http://localhost:4567/projects/1/tasks" \
     -H "Accept: application/json" \
     -w "\nHTTP Status: %{http_code}\n"

# get non existing project todo relationship

echo $'\n================================================================================='
curl -X GET "http://localhost:4567/projects/20/tasks" \
     -H "Accept: application/json" \
     -w "\nHTTP Status: %{http_code}\n"

echo $'\n================================================================================='

# Head request for project todo relationship
echo "==== HEAD Request for Project-Todo Relationship ===="
curl -I "http://localhost:4567/projects/1/tasks" \
     -H "Accept: application/json" \
     -w "\nHTTP Status: %{http_code}\n"

echo $'\n================================================================================='

# Post request for project todo relationship
echo "==== POST to Create Project-Todo Relationship ===="
curl -X POST "http://localhost:4567/projects/1/tasks" \
     -H "Content-Type: application/json" \
     --data-raw '{"id": "1"}' \
     -w "\nHTTP Status: %{http_code}\n"

echo $'\n================================================================================='

# Delete request for project todo relationship
echo "==== DELETE Existing Project-Todo Relationship (ID 1) ===="
curl -X DELETE "http://localhost:4567/projects/1/tasks/1" \
     -H "Accept: application/json" \
     -w "\nHTTP Status: %{http_code}\n"

echo $'\n================================================================================='

# Fer project-category relationship
echo "==== Fetching Categories for Project with ID 1 ===="
curl -X GET "http://localhost:4567/projects/1/categories" \
     -H "Accept: application/json" \
     -w "\nHTTP Status: %{http_code}\n"

echo $'\n================================================================================='

# Get non existing project category relationship
echo "==== Fetching Categories for Non-Existent Project (ID 20) ===="
curl -X GET "http://localhost:4567/projects/20/categories" \
     -H "Accept: application/json" \
     -w "\nHTTP Status: %{http_code}\n"

echo $'\n================================================================================='

# Head request for project category relationship
echo "==== HEAD Request for Project-Category Relationship ===="
curl -I "http://localhost:4567/projects/1/categories" \
     -H "Accept: application/json" \
     -w "\nHTTP Status: %{http_code}\n"

echo $'\n================================================================================='

# Post request for project category relationship

echo "==== POST to Create Project-Category Relationship ===="
curl -X POST "http://localhost:4567/projects/1/categories" \
     -H "Content-Type: application/json" \
     --data-raw '{"id": "1"}' \
     -w "\nHTTP Status: %{http_code}\n"

echo $'\n================================================================================='

# Delete request for project category relationship
echo "==== DELETE Existing Project-Category Relationship (ID 1) ===="
curl -X DELETE "http://localhost:4567/projects/1/categories/1" \
     -H "Accept: application/json" \
     -w "\nHTTP Status: %{http_code}\n"

echo $'\n================================================================================='