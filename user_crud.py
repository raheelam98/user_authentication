# user_service_auth -  app/controllers/user_crud.py

from fastapi import HTTPException
from sqlmodel import select, Session
from app.db.db_connector import DB_SESSION
from app.models.user_model import User, UserUpdateModel, UserModel
from app.utlis.auth import passwordIntoHash


# Function to retrieve user data from the database
def get_user_from_db(session: DB_SESSION):
    # Create a SQL statement to select all users
    statement = select(User)
    # Execute the statement and get the list of users
    user_list = session.exec(statement).all()

    # If no users found, raise an HTTPException with status code 404
    if not user_list:
        raise HTTPException(status_code=404, detail="User Not Found")
    # Otherwise, return the list of users
    else:
        return user_list
    
### ========================= *****  ========================= ###

# Function to add a user into the database
def add_user_into_db(form_data: UserModel, session: Session):
    # Create a new User object using the details provided in form_data
    user = User(**form_data.model_dump())

    user.user_password = passwordIntoHash(form_data.user_password)

    # Add the user to the session
    session.add(user)
    # Commit the session to save the user to the database
    session.commit()
    # Refresh the session to retrieve the new user data
    session.refresh(user)
    print("New user added:", user)
    return user    

### ========================= *****  ========================= ###

def update_user_from_db(selected_id: int, update_form_data: UserUpdateModel, session: DB_SESSION):
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
    selected_user.user_address = update_form_data.user_address
    selected_user.user_country = update_form_data.user_country
    selected_user.phone_number = update_form_data.phone_number

    # Add the updated user to the session
    session.add(selected_user)
    # Commit the session to save the changes to the database
    session.commit()
    # Refresh the session to retrieve the updated user data
    session.refresh(selected_user)
    return selected_user

### ========================= *****  ========================= ###

# Function to delete a user from the database
def delete_user_from_db(delete_id: int, session: DB_SESSION):
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