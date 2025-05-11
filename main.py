from fastapi import FastAPI, HTTPException
from fastapi import Depends, Query, Request
from typing import List, Annotated, Optional
from models import FullUser, UserResponse, Token, BookCreate, BookResponse, BookInternal, BookUpdate
from passlib.context import CryptContext
from jose import jwt, JWTError
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from datetime import datetime, timedelta, timezone

from fastapi.responses import JSONResponse, Response
from dicttoxml import dicttoxml

# These would be in a CONFIG file with gitignore but for practice I'll keep it here 
SECRET_KEY = "1cf4ebd192b607bcb8860ca32ea052dc7e9f6f80e3655a6ae2c0b5595da4a7c8"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

app = FastAPI()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# our in memory database of users
users_db: List[FullUser] = [
    FullUser(
        id = 1,
        username = "Bobby",
        encrpt_password = "123abc",
        author_pseudonym = "bobcat"
    ),
    FullUser(
        id = 2,
        username = "Ted",
        encrpt_password = "123abc",
        author_pseudonym = "teddybear"
    )
]

# in memory database of books
books_db: List[BookInternal] = [
    BookInternal(
        id=1,
        title="The Rise of the Wookie",
        description="Start of the new galactic superpower lead by Emperor Chewbaca.",
        cover_image="https://static.wikia.nocookie.net/starwars/images/7/73/WookieeTrio-MtHChewbacca.png/revision/latest?cb=20230810013600",
        price=16.50,
        author_username="Chewy",
        author_pseudonym="furball"
    ),
    BookInternal(
        id=2,
        title="Icile of Hoth",
        description="A frozen wookie found on the ice planet Hoth will awaken!",
        cover_image="http://example.com/covers/endor.jpg",
        price=21.89,
        author_username="Luke",
        author_pseudonym="skywalker"
    )
]

# lets encrypt the password
password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# this will handle printing response in json or xml
def custom_response(data, content_type: str = "application/json"):
    
    if "xml" in content_type.lower():
        xml_bytes = dicttoxml(data, custom_root='response', attr_type=False)
        return Response(content=xml_bytes, media_type="application/xml")
    return data

# I couldn't fast api library to serialize output so using my custom fuction to serial users
def serialize_user(user):
    return {
        "id": user.id,
        "username": user.username,
        "author_pseudonym": user.author_pseudonym
    }

# Custom fuction to serialize books
def serialize_book(book):
    return {
        "id": book.id,
        "title": book.title,
        "description": book.description,
        "cover_image": book.cover_image,
        "author_username": book.author_username,
        "author_pseudonym": book.author_pseudonym,
        "price": book.price
    }

# hashing passeord for securly storing in database
def hashed_password(password: str) -> str:
    return password_context.hash(password)

# Auth function to check if user is in db
def authenticate_user(username: str, password: str):
    user = next((u for u in users_db if u.username == username), None)

    # verifying if password entered was correct 
    if not user or not password_context.verify(password, user.encrpt_password):
        return None
    return user

# Creating JWT token --> taken from FAST API docs
def create_access_token(data: dict, expires_delta: timedelta) -> str:
    
    to_encode = data.copy()
    
    expire = datetime.now(timezone.utc) + expires_delta
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

# gets the current user for comparison with Author!
def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]) -> FullUser:
    
    credentials_exception = HTTPException(
        status_code=401,
        detail="Invalid Token: No username."
    )

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if username is None:
            raise credentials_exception   # Throw an error if JWT token is not connected to the current user
    except JWTError:
        raise credentials_exception
    
    # token is valid so return the current user
    for user in users_db:
        if user.username == username:
            return user
    user = None
    return user

@app.post("/api/v1/login", response_model=Token)
async def login_for_access_token(request: Request, form_data: Annotated[OAuth2PasswordRequestForm, Depends()],) -> Token:
    
    # Authenticate if user exists first (will need authenticate fuction)
    user = authenticate_user(form_data.username, form_data.password)
    content_type = request.headers.get("accept", "application/json")  # 2nd arg sets default to json

    # if user cred is wrong raise error 401 
    if not user:
        raise HTTPException(
            status_code=401,
            detail="Incorrect username or password"
            # headers={"WWW-Authenticate": "Bearer"},
        )    

    # create the token using a expire limit of 30 mins
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    return custom_response(Token(access_token=access_token, token_type="bearer"),content_type)



@app.get("/")
async def root(request: Request):
    
    # just a tester 
    data = {"hello": "world"}
    content_type = request.headers.get("accept", "application/json") 
    return custom_response(data, content_type)


@app.get("/api/v1/users", response_model=List[UserResponse])
async def fetch_users(request: Request):

    content_type = request.headers.get("accept", "application/json")  # 2nd arg sets default to json
    
    # serialize users one by 1 and sent them for output
    serialized_users = [serialize_user(user) for user in users_db]
    return custom_response(serialized_users, content_type)
    # return users_db

@app.post("/api/v1/users", response_model=UserResponse)
async def register_user(user: FullUser, request: Request):
    
    # check if usename already exists and throw error
    for u in users_db:
        if u.username == user.username:
            raise HTTPException(status_code=400, detail="Username taken")
    
    # create new user object for database
    new_user = FullUser(
        id = len(users_db) + 1,  # we can use UUID for better unique Id's
        username = user.username,
        encrpt_password = hashed_password(user.encrpt_password),
        author_pseudonym = user.author_pseudonym
    )
    users_db.append(new_user)  # add to database
        
    content_type = request.headers.get("accept", "application/json")  # 2nd arg sets default to json
    serialized_users = serialize_user(new_user)
    return custom_response(serialized_users, content_type)

# not mentioned but I implemented it for practice
@app.delete("/api/v1/users/{user_id}")
async def delete_user(user_id: int, request: Request):
    
    content_type = request.headers.get("accept", "application/json") 

    for user in users_db:
        if user_id == user.id:
            users_db.remove(user)
            detail = {"detail": "User deleted!"}
            return custom_response(detail, content_type) 
    raise HTTPException(
        status_code=404,
        detail=f"User with id: {user_id} does not exist"
    )

@app.get("/api/v1/books", response_model=List[BookResponse])
async def list_books(request: Request, q: Optional[str] = Query(default=None, description="Search using Title or Description")):
    content_type = request.headers.get("accept", "application/json")
    
    # if they choose to query
    if q:
        # have a list of books where the query is satisfied 
        matched_books = [
            book
            for book in books_db
            if q.lower() in book.title.lower() or q.lower() in book.description.lower()
        ]

        # if no books found raise exception
        if not matched_books:
            raise HTTPException(status_code=404, detail=f"No books found with the word {q}")

        serialized = [serialize_book(book) for book in matched_books]
        return custom_response(serialized, content_type)
    
    # return all books for general get
    serialized_books = [serialize_book(book) for book in books_db]
    return custom_response(serialized_books, content_type)


@app.get("/api/v1/books/{book_id}", response_model=BookResponse)
async def get_book(request: Request, book_id: int):

    content_type = request.headers.get("accept", "application/json")  # 2nd arg sets default to json

    # get specific book based on Id
    for book in books_db:
        if book.id == book_id:
            return custom_response(serialize_book(book), content_type)
    raise HTTPException(
        status_code=404,
        detail="Book not found! Invalid Id"
    )

@app.post("/api/v1/books", response_model=BookResponse)
def create_book(request: Request, book: BookCreate, current_user: Annotated[FullUser, Depends(get_current_user)]): 
    content_type = request.headers.get("accept", "application/json")  # 2nd arg sets default to json
    
    # Make sure Vader can't up load books!!!
    if current_user.username.lower() == "darth vader" or current_user.username.lower() == "_darth vader_":
        raise HTTPException(status_code=403, detail="Darth Vader is not allowed to publish on Wookie Books.")

    # create new book object
    new_book = BookInternal(
        id=len(books_db)+1,
        title=book.title,
        description=book.description,
        cover_image=book.cover_image,
        price=book.price,
        author_username=current_user.username,
        author_pseudonym=current_user.author_pseudonym
    )
    books_db.append(new_book)
    return custom_response(serialize_book(new_book), content_type)

@app.put("/api/v1/books/{book_id}", response_model=BookResponse)
async def update_book(request: Request, book_id: int, updated_book: BookUpdate, current_user: Annotated[FullUser, Depends(get_current_user)]):
    
    content_type = request.headers.get("accept", "application/json")  # 2nd arg sets default to json
   
    # check if book Id is in books_db else make book = None
    book = next((b for b in books_db if b.id == book_id), None)

    # only allow the authors to update books!
    if book is None:
        raise HTTPException(status_code=404, detail="Book not found.")
    if book.author_username != current_user.username:
        raise HTTPException(status_code=403, detail="Forbidden! Not your book.")
    
    # check which fields are updated
    if updated_book.title is not None:
        book.title = updated_book.title
    if updated_book.description is not None:
        book.description = updated_book.description
    if updated_book.cover_image is not None:
        book.cover_image = updated_book.cover_image
    if updated_book.price is not None:
        book.price = updated_book.price
    
    return custom_response(serialize_book(book), content_type)

@app.delete("/api/v1/books/{book_id}")
async def delete_book(request: Request, book_id: int, current_user: Annotated[FullUser, Depends(get_current_user)]):
    
    content_type = request.headers.get("accept", "application/json")  # 2nd arg sets default to json

    # delete a book based on Id
    deleted_book = None
    for book in books_db:
        if book.id == book_id:
            deleted_book = book
            break
    
    # only authors can delete their own books
    if deleted_book is None:
        raise HTTPException(status_code=404, detail="Book not found in database")
    if deleted_book.author_username != current_user.username:
        raise HTTPException(status_code=403, detail="Forbidden! Not allowed to delete someone else's book!")
    
    books_db.remove(deleted_book)

    return custom_response({"detail": "Book deleted!"}, content_type)