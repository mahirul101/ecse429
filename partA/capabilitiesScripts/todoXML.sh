echo "get all todo"
curl -X GET 'http://localhost:4567/todos' \
     -H 'Accept: application/xml' \
     -w "HTTP Status: %{http_code}\n"

echo $'\n================================================================================='

# echo "==== Sending HEAD Request to /todos ===="

curl -I 'http://localhost:4567/todos' \
     -H 'Accept: application/XML' \
     -w "HTTP Status: %{http_code}\n"
echo $'\n================================================================================='

echo "==== Creating a New Todo (POST to /todos) ===="
curl -X POST 'http://localhost:4567/todos' \
     -H 'Accept: application/xml' \
     -H 'Content-Type: application/xml' \
     --data-raw '<todo>
                    <description>Buy groceries</description>
                    <doneStatus>false</doneStatus>
                    <title>Groceries</title>
                 </todo>' \
     -w "HTTP Status: %{http_code}\n"

echo $'\n================================================================================='

echo "==== Fetching Todo with ID 1 ===="
curl -X GET 'http://localhost:4567/todos/1' \
     -H 'Accept: application/xml' \
     -w "HTTP Status: %{http_code}\n"

echo $'\n================================================================================='

echo "==== Fetching Non-Existent Todo (ID 20) ===="
curl -X GET 'http://localhost:4567/todos/20' \
     -H 'Accept: application/xml' \
     -w "HTTP Status: %{http_code}\n"

echo $'\n================================================================================='

# Put request for todo
echo "==== Updating Todo with ID 1 ===="

curl -X PUT 'http://localhost:4567/todos/3' \
     -H 'Accept: application/xml' \
     -H 'Content-Type: application/xml' \
     --data-raw '<todo>
                    <description>Buy groceries</description>
                    <doneStatus>true</doneStatus>
                    <title>Groceries</title>
                 </todo>' \
     -w "HTTP Status: %{http_code}\n"

echo $'\n================================================================================='

echo "==== HEAD Request for Todo with ID 1 ===="
curl -I 'http://localhost:4567/todos/1' \
     -H 'Accept: application/xml' \
     -w "HTTP Status: %{http_code}\n"

echo $'\n================================================================================='

# Update non existing todo
echo "==== Updating Non-Existent Todo (ID 20) ===="
curl -X PUT 'http://localhost:4567/todos/20' \
     -H 'Accept: application/xml' \
     -H 'Content-Type: application/xml' \
     --data-raw '<todo>
                    <description>Buy groceries</description>
                    <doneStatus>true</doneStatus>
                    <title>Groceries</title>
                 </todo>' \
     -w "HTTP Status: %{http_code}\n"

echo $'\n================================================================================='

echo "==== Deleting Todo with ID 2 ===="
curl -X DELETE 'http://localhost:4567/todos/2' \
     -H 'Accept: application/xml' \
     -w "HTTP Status: %{http_code}\n"

echo $'\n================================================================================='

echo "==== Attempting to Delete Non-Existent Todo (ID 20) ===="
curl -X DELETE 'http://localhost:4567/todos/20' \
     -H 'Accept: application/xml' \
     -w "HTTP Status: %{http_code}\n"


echo $'\n================================================================================='

echo "==== Fetching Todo with ID 1 ===="
curl -X GET 'http://localhost:4567/todos/1' \
     -H 'Accept: application/xml' \
     -w "HTTP Status: %{http_code}\n"

echo $'\n================================================================================='

# do a get head and post request for http://localhost:4567/todos/:id/categories  
echo "==== Fetching Categories for Todo with ID 1 ===="
curl -X GET 'http://localhost:4567/todos/1/categories' \
     -H 'Accept: application/xml' \
     -w "HTTP Status: %{http_code}\n"

echo $'\n================================================================================='

# perfrom get /todos/:id/taskof with a non existing id 20
echo "==== Fetching TaskOf for Todo with ID 20 ===="
curl -X GET 'http://localhost:4567/todos/20/taskof' \
     -H 'Accept: application/xml' \
     -w "\nHTTP Status: %{http_code}\n"

