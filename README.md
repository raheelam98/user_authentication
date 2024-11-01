# Online Mart - User Service

## DATABASE_URL 

.env  (Write secret credential.)

```bash
DATABASE_URL=postgresql://database_username:password@hostname:port/database_name?sslmode=require
```

**Note:-** When copying the database URL (DB_URL), ensure that only the owner has access to add, update, and delete data. Developers should have limited write access.

Note :- default port : 5432

## Contecting with database

setting.py

```bash
from starlette.config import Config
from starlette.datastructures import Secret

try:
    config = Config(".env")
except FileNotFoundError:
    config = Config()  

DATABASE_URL = config("DATABASE_URL", cast=Secret)
```

**======================== ** ** ========================**

## Create Database Schema using SQLModel

UserBase defines the shared attributes for a user, while User extends it to represent a database table with user_id as the primary key.

```bash
# Define the UserBase and User models
class UserBase(SQLModel):
    user_name: str
    user_address: str
    user_email: str
    user_password: str    

class User(UserBase, table=True):
    user_id: Optional[int] = Field(default=None, primary_key=True)
```

**======================== ** ** ========================**

## Create a Table with SQLModel - Use the Engine

```bash
# Set up the database connection
connection_string = str(DATABASE_URL).replace(
    "postgresql", "postgresql+psycopg"
)

# Create an engine for the database connection
engine = create_engine(connection_string, connect_args={}, pool_recycle=300)

# Function to create the database and tables
async def create_db_and_tables():
    print(f'Creating Tables ...')
    # Create all the database tables
    SQLModel.metadata.create_all(engine)

# function, before the yield, will be executed before the application starts
# create session to get memory space in db
def get_session():
    with Session(engine) as session:
        yield session

# Dependency injection to get a session
DB_Session = Annotated[Session, Depends(get_session)]
```

## FastAPI

```bash
# Lifespan function provided by FastAPI (creates DB table at program startup)
# It creates the table only once; if the table already exists, it won't create it again
async def life_span(app: FastAPI):
    print("Call create tables function during lifespan startup...")
    await create_db_and_tables()  # Properly await table creation
    yield  # Lifespan generator is working correctly

# Create FastAPI instance
app = FastAPI(lifespan=life_span, title='Product API')

```

**Explanation**

#### Contection String

```bash
connection_string = str(DATABASE_URL).replace("postgresql", "postgresql+psycopg")
``` 

This code modifies the DATABASE_URL so it can use the psycopg driver when connecting to a PostgreSQL database:

**str(DATABASE_URL):** Converts DATABASE_URL into a string representation, which is necessary for the replacement to be performed.

**.replace("postgresql", "postgresql+psycopg"):** Changes "postgresql" to "postgresql+psycopg" in the connection string. This ensures that SQLAlchemy knows to use the psycopg driver to connect to the PostgreSQL database.

**psycopg** driver is a popular and efficient library for interacting with PostgreSQL databases in Python

#### create a connection to the database

```bash
engine = create_engine(connection_string, connect_args={}, pool_recycle=300)
``` 

**create_engine()** SQLModel Function (create a connection to the database)

**Detail Description**

**connection_string:** Specifies the database URL (e.g., the type of database and its location).

**connect_args={}:** Additional arguments for the connection (often used for settings specific to the type of database).

**pool_recycle=300:** Prevents stale connections by recycling (re-establishing) them every 300 seconds to avoid issues like timeout.

####  Create all tables defined in the model

```bash
SQLModel.metadata.create_all(engine)
``` 

**SQLModel.metadata.create_all()**

**.metadata:** attribute keeps track of all the models (tables)

**.create_all():** Uses .metadata to create the tables in your database

**.engine:** SQLAlchemy database engine that points to your database.

**Detail Description**

SQLModel: It’s a library built on top of SQLAlchemy and Pydantic that simplifies working with SQL databases in Python, commonly used with FastAPI for defining database models.

.metadata: This attribute of SQLModel contains metadata about all the defined tables, such as table names and their columns. It acts as a registry for your models.

.create_all(): This method, when called, uses the metadata to generate SQL commands that create the necessary tables in the connected database. Essentially, it will ensure all your defined models have corresponding tables.

### Session

```bash
def get_session():
    with Session(engine) as session:
        yield session
``` 

This function creates a session object using the provided engine for database connectivity, and it yields this session. It ensures that the session is properly created and closed after use. 

**- with** statement ensures that resources are properly managed, like automatically closing the session after it's used.

**- yield** allows a function to return a value and then pause its execution, resuming right where it left off the next time it’s called. This is what makes a generator function. It’s perfect for situations where you want to iterate through a sequence without storing the entire thing in memory

The code in the function before yield will be executed each time the generator is called.

### Lifespan

Lifespan function provided by FastAPI (creates DB table at program startup)
It creates the table only once; if the table already exists, it won't create it again

```bash
async def life_span(app: FastAPI):
    print("Creating tables during lifespan startup...")
    await create_db_and_tables()  # Properly await table creation
    yield  # Lifespan generator is working correctly
``` 

### Create FastAPI instance

```bash
app = FastAPI(lifespan=life_span, title='Fast API')
``` 

**======================== ** ** ========================**

## Retrive Data

```bash
# Function to retrieve user data from the database
def get_user_from_db(session: DB_Session):
    # Create a SQL statement to select all users
    statement = select(User)
    # Execute the statement and get the list of users
    user_list = session.exec(statement).all()

    # If no users found, raise an HTTPException with status code 404
    if not user_list:
        raise HTTPException(status_code=404, detail="Not Found")
    # Otherwise, return the list of users
    else:
        return user_list

# API endpoint to get users
@app.get('/api/get_user')
def get_user(session: DB_Session):
    # Call the function to retrieve user data from the database
    users = get_user_from_db(session)
    # Return the list of users
    return users
```

**Explanation**

#### Retrieve data from the database

```bash
statement = select(User)
user_list = session.exec(statement).all()
```

**select(User)** creates a query to select all records from the User table.

**user_list = session.exec(statement).all()** executes the query and retrieves all results as a list by calling .all()

Note :-  **.all()** is used on the result of session.exec(statement) to get a list of all rows immediately, instead of returning an iterable.

## Create Data 

```bash
# Function to add a user into the database
def add_user_into_db(form_data: UserBase, session: Session):
    # Create a new User object using the details provided in form_data
    user = User(**form_data.model_dump())

    # Add the user to the session
    session.add(user)
    # Commit the session to save the user to the database
    session.commit()
    # Refresh the session to retrieve the new user data
    session.refresh(user)
    print("New user added:", user)
    return user

# POST route to add a new user
@app.post('/api/add_user')
def add_user(new_user: UserBase, session: DB_Session):
    # Call function to add user
    add_user = add_user_into_db(new_user, session)
    print("Add user route ...", add_user)
    return add_user
```

**Explanation**

#### Get Form Data

**creates a new user object using the details provided in form_data.**

```bash
User(**form_data.model_dump())
``` 

form_data.model_dump():- return a dictionary of the data stored in form_data

(**form_data.model_dump()) :- unpacks the form_data dictionary into keyword arguments

**Note**  ** (double asterisk): unpacks a dictionary into keyword arguments.

**Detail Description**

**1- Pydantic Model:** User instance (form_data) holds user details.

**2- Convert to Dictionary:** form_data.model_dump() converts the instance to a dictionary.

**3- Dictionary Unpacking:** **form_data.model_dump() unpacks the dictionary into keyword arguments.

**4- Create User Object:** User(**form_data.model_dump()) creates a new User object with the provided details.

**model_dump()** method in Pydantic :- converts a model instance into a dictionary with the model's attribute names as keys and their corresponding values.

## Update Record 

```bash
def update_user_from_db(selected_id: int, update_form_data: UserUpdateModel, session: DB_Session):
    # Create a SQL statement to select the user with the given ID
    statement = select(User).where(User.user_id == selected_id)
    # Execute the statement and get the selected user
    selected_user = session.exec(statement).first()

    # If the user is not found, raise an HTTPException with status code 404
    if not selected_user:
        raise HTTPException(status_code=404, detail="Not Found")
    
    # Update the user's details with the data from the form
    # databse               = form data
    selected_user.user_name = update_form_data.user_name
    selected_user.user_password = update_form_data.user_password
    selected_user.user_address = update_form_data.user_address

    # Add the updated user to the session
    session.add(selected_user)
    # Commit the session to save the changes to the database
    session.commit()
    # Refresh the session to retrieve the updated user data
    session.refresh(selected_user)
    return selected_user

@app.put('/api/update_user')
def update_user(id:int, user_detail: UserUpdateModel, session: DB_Session):
    # Call the function to retrieve data from the database
    user = update_user_from_db(id, user_detail, session)
    return user
```

**Explanation**

#### Update Form Data

```bash
statement = select(User).where(User.user_id == selected_id)
selected_user = session.exec(statement).first()
``` 

**select(User)**: Specifies that you want to select data from the User table.

**.where()** filter rows 

**.where(User.user_id == selected_id)**: Adds a condition to filter the results to only include rows where user_id matches selected_id.

Executing Raw SQL :- **session.exec()** to run raw SQL queries

## Delete Record

```bash
# Function to delete a user from the database
def delete_user_from_db(delete_id: int, session: DB_Session):
    # Retrieve the user from the database using the given ID
    user = session.get(User, delete_id)

    # If the user is not found, raise an HTTPException with status code 404
    if not user:
        raise HTTPException(status_code=404, detail="Not Found")
    
    # Delete the user from the session
    session.delete(user)
    # Commit the session to save the changes to the database
    session.commit()
    return 'User deleted'

# API endpoint to delete a user
@app.delete('/api/delete_user')
def delete_user(id: int, session: DB_Session):
    # Call function to delete the user from the database
    deleted_user = delete_user_from_db(id, session)
    return f'User id {id} has been successfully deleted'
```

**Explanation**

Retrieves a User object by its primary key

```bash
session.get(User, delete_id)
``` 

**session.get(User, delete_id)** retrieves a specific record from the User table where the primary key matches the value of **delete_id**. If a matching record is found, it returns the corresponding User object; otherwise, it returns None.

**get()** is a versatile method that enhances both dictionary manipulations and HTTP requests in Python.

**======================== ** ** ========================**

## Tutorials

[First Steps](https://fastapi.tiangolo.com/tutorial/first-steps/)

[Create a Table with SQLModel - Use the Engine](https://sqlmodel.tiangolo.com/tutorial/create-db-and-table/#last-review)

[Read Data - SELECT](https://sqlmodel.tiangolo.com/tutorial/select/#review-the-code)

[Can Pydantic model_dump() return exact type?](https://stackoverflow.com/questions/77476105/can-pydantic-model-dump-return-exact-type)

[Models with Relationships in FastAPI](https://sqlmodel.tiangolo.com/tutorial/fastapi/relationships/)

[Filter Data - WHERE](https://sqlmodel.tiangolo.com/tutorial/where/)

[Update Data - UPDATE](https://sqlmodel.tiangolo.com/tutorial/update/#read-from-the-database)


[SQLModel : Delete Data - DELETE](https://sqlmodel.tiangolo.com/tutorial/delete/#review-the-code)

[Delete Data - DELETE](https://sqlmodel.tiangolo.com/tutorial/delete/)

**======================== ** ** ========================**

## Tutorials Details  

**SQLModel** (ORM)

[How to re-run failed tests and maintain state between test runs](https://docs.pytest.org/en/stable/how-to/cache.html)

[OAuth2 with Password (and hashing), Bearer with JWT tokens](https://fastapi.tiangolo.com/tutorial/security/oauth2-jwt/?h=jwt)


**JWT means "JSON Web Tokens"** (It is not encrypted), Install python-jose

- jwt token decode  # Decoding the token
-decoded_token = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])  

**======================== ** ** ========================**
