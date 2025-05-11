### Objective

Practice building a REST API using FastAPI - Not yet complete

### What is this

Star Wars bookstore marketplace

### Tasks

-   Implement a REST API returning JSON or XML based on the `Content-Type` header
-   Implement a custom user model with a "author pseudonym" field
-   Implement a book model. Each book should have a title, description, author (your custom user model), cover image and price
    -   Choose the data type for each field that makes the most sense
-   Provide an endpoint to authenticate with the API using username, password and return a JWT
-   Implement REST endpoints for the `/books` resource
    -   No authentication required
    -   Allows only GET (List/Detail) operations
    -   Make the List resource searchable with query parameters
-   Provide REST resources for the authenticated user
    -   Implement the typical CRUD operations for this resource
    -   Implement an endpoint to unpublish a book (DELETE)
-   Implement API tests for all endpoints

Requirements to test:

pip install fastapi
pip install uvicorn
pip install python-jose[cryptography] 
pip install passlib[bcrypt]
pip install pytest
pip install httpx
pip install dicttoxml

Once all is installed run "pytest" in the directory where all files are

1. https://fastapi.tiangolo.com/tutorial/
2. https://www.getorchestra.io/guides/fastapi-response-model-a-comprehensive-guide
3. https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Status
4. https://docs.pydantic.dev/latest/
5. Thunder Client on VS Code for API testing
