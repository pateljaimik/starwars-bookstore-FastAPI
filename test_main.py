from fastapi.testclient import TestClient
from main import app  

client = TestClient(app)

# get list of users
def test_get_users():
    response = client.get("/api/v1/users")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_get_users_xml():
    response = client.get(
        "/api/v1/users",
        headers={"Accept": "application/xml"}
    )
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/xml"
    assert "<response>" in response.text

# test creating a new user
def test_post_user():
    response = client.post("/api/v1/users", json={
        "username": "Batman",
        "encrpt_password": "123abc",
        "author_pseudonym": "darknight"
    })
    assert response.status_code == 200
    assert response.json()["username"] == "Batman"

# test for usernames already taken
def test_post_user_taken():
    response = client.post("/api/v1/users", json={
        "username": "Batman",
        "encrpt_password": "1asf23abc",
        "author_pseudonym": "darknight"
    })
    assert response.status_code == 400
    assert response.json()["detail"] == "Username taken"

# test loging in 
def test_login():
    global access_token  # so we can use it later 
    response = client.post("/api/v1/login", data={
        "username": "Batman",
        "password": "123abc"
    })
    assert response.status_code == 200
    access_token = response.json()["access_token"]
    print(access_token)
    assert access_token is not None

# add a book to the db
def test_post_book():
    response = client.post(
        "/api/v1/books",
        json={
            "title": "The Death Star Blueprint",
            "description": "The planet destroyer",
            "cover_image": "http://example.com/covers/endor.jpg",  # must be a valid URL
            "price": 19.99
        },
        headers={"Authorization": f"Bearer {access_token}"}
    )
    assert response.status_code == 200
    assert response.json()["title"] == "The Death Star Blueprint"

# get a list of books
def test_get_books():
    response = client.get("/api/v1/books")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

# get a speific of books
def test_get_books():
    response = client.get("/api/v1/books/3")
    assert response.status_code == 200

# test the query param for a book which exists 
def test_search_books_query_existing_data():
    response = client.get("/api/v1/books?q=wookie")
    assert response.status_code == 200

    books = response.json()
    # assert isinstance(books, list)
    assert len(books) > 0
    for book in books:
        assert "wookie" in book["title"].lower() or "wookie" in book["description"].lower()

def test_search_books_query_non_existing_data():
    q= "yoda"
    response = client.get(f"/api/v1/books?q={q}")
    assert response.status_code == 404
    assert response.json()["detail"] == f"No books found with the word {q}"

# # update a book that is pre-existing and not Batman's (shouldnt be allowed)
def test_update_book_fail():
    response = client.put(
        "/api/v1/books/1",
        json={
            "title": "Wookie Adventures Updated",
            "price": 17.99,
            "description": "Now with more jungle!"
        },
        headers={"Authorization": f"Bearer {access_token}"}
    )
    assert response.status_code == 403
    assert response.json()["detail"] == "Forbidden! Not your book."

# update a book that is yours aka. Batman
def test_update_book_success():
    response = client.put(
        "/api/v1/books/3",
        json={
            "title": "The Death Star Blows Up",
            "price": 12.99
        },
        headers={"Authorization": f"Bearer {access_token}"}

    )
    print("\n",access_token)
    assert response.status_code == 200
    assert response.json()["title"] == "The Death Star Blows Up"

# try deleting a book in wich YOU ARE NOT THE AUTHOR
def test_delete_book():
    response = client.delete(
        "/api/v1/books/1",
        headers={"Authorization": f"Bearer {access_token}"}
    )
    assert response.status_code == 403
    assert response.json()["detail"] == "Forbidden! Not allowed to delete someone else's book!"

# batman deleting his own book!
def test_delete_book():
    response = client.delete(
        "/api/v1/books/3",
        headers={"Authorization": f"Bearer {access_token}"}
    )
    assert response.status_code == 200
    assert response.json()["detail"] == "Book deleted!"