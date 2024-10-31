# user_service_auth - db_connector.py

from app.settings import DATABASE_URL
from sqlmodel import create_engine, SQLModel, Session

from typing import Annotated
from fastapi import Depends

### ========================= *****  ========================= ###

# Set up the database connection
connection_string = str(DATABASE_URL).replace(
    "postgresql", "postgresql+psycopg"
)

# Create an engine for the database connection
engine = create_engine(
    connection_string, connect_args={}, pool_recycle=300
)

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
DB_SESSION = Annotated[Session, Depends(get_session)]

