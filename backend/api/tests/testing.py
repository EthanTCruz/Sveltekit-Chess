from unittest import mock,Mock
from api.src.dependencies import *
from sqlalchemy.orm import Session
from api.src.models import *


hashed_password = "$2b$12$204BFdf6EeEKNtty6dOlfeiumypfvephe5pmxjv8WjEBXVotSRsdC"

# Create a list of mock User objects
mock_user1 = UserDB(id=1,username="user1",hashed_password=hashed_password) 
mock_user2 = UserDB(id=2,username="user2",hashed_password=hashed_password)

@mock.patch("api.src.dependencies.SessionLocal")
def test_get_user(mocked_session):

    # Configure the mock session to return mock_users
    mock_session = mocked_session.return_value.__enter__.return_value
    mock_session.query.return_value.filter.return_value.first.return_value = mock_user1

    # Now, when you call your function that fetches users, it will return mock_users
    result1 = get_user(db=mock_session,username=mock_user1.username)

    assert result1 == mock_user1


def test_verify_password():
    # Test that the password verification works correctly

    plain_password = "password"
    assert verify_password(plain_password, hashed_password) == True  # or False, depending on your hashing logic

@mock.patch("api.src.dependencies.SessionLocal")
def test_get_user(mocked_session):
    # Mock the database session
    mock_session = mocked_session.return_value.__enter__.return_value
    mock_session.query.return_value.filter.return_value.first.return_value = "Mocked User"

    # Test the get_user function
    user = get_user(mock_session, "user1")
    assert user == "Mocked User"
    mock_session.query.assert_called_once()



@mock.patch("api.src.dependencies.SessionLocal")
def player1_v_player2(mocked_session):
    # Mock the database session
    password = "password"
    mock_session = mocked_session.return_value.__enter__.return_value
    mock_session.query.return_value.filter.return_value.first.return_value = "Mocked User"

    user1 = authenticate_user(mock_session,"user1",password)
    user2 = authenticate_user(mock_session,"user2",password)

    token1 = create_access_token(data = {"sub": user1.username})
    token2 = create_access_token(data = {"sub": user2.username})


    
    match1 = matchfinder(token=token1,db=mock_session)
    match2 = matchfinder(token=token2,db=mock_session)

    match1 = matchfinder(token=token1,db=mock_session)

    assert match1 == match2

    mock_session.query.assert_called_once()

