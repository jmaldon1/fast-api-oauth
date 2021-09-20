from typing import Dict

from fastapi import status
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from oauth_app.app import schemas
from oauth_app.app import crud

from tests.utils import authentication_token_from_email


def test_get_root(client: TestClient):
    response = client.get("/")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"message": "Hello World"}


def test_create_user(client: TestClient):
    email = "josh@example.com"
    full_name = "Josh Doe"
    password = "fake_pass_123"
    data = {"email": email, "full_name": full_name, "password": password}
    expected = {
        "id": 2,
        "email": "josh@example.com",
        "full_name": "Josh Doe",
        "is_active": True,
        "is_superuser": False,
    }

    resp = client.post("/users", json=data)
    actual = resp.json()
    assert resp.status_code == status.HTTP_200_OK
    assert expected == actual


def test_login_user(client: TestClient, db: Session):
    email = "matt@example.com"
    full_name = "Matt Doe"
    password = "fake_pass_123"
    login_data = {
        "username": email,
        "password": password,
    }

    user_in = schemas.UserCreate(email=email, full_name=full_name, password=password)
    crud.create_user(db, user_in)
    resp = client.post("/token", data=login_data)
    actual_token = resp.json()
    assert resp.status_code == status.HTTP_200_OK
    assert "access_token" in actual_token
    assert actual_token["access_token"]


def test_get_authenticated_active_user(client: TestClient, db: Session):
    email = "john@example.com"
    full_name = "John Doe"
    password = "fake_pass_123"
    expected = {
        "id": 4,
        "is_active": True,
        "email": "john@example.com",
        "full_name": "John Doe",
        "is_superuser": False,
    }

    # This will create the user if it doesn't exist.
    user_token_headers = authentication_token_from_email(
        client=client, db=db, email=email, password=password, full_name=full_name
    )
    resp = client.get("/users/me", headers=user_token_headers)
    actual = resp.json()
    assert resp.status_code == status.HTTP_200_OK
    assert expected == actual


def test_get_authenticated_superuser(client: TestClient, db: Session):
    """Superuser should already be created from when we initialized the DB."""
    email = "admin@example.com"
    password = "admin"
    expected = {
        "email": "admin@example.com",
        "full_name": None,
        "is_active": True,
        "is_superuser": True,
        "id": 1,
    }
    superuser_token_headers = authentication_token_from_email(
        client=client, db=db, email=email, password=password
    )
    resp = client.get("/users/me", headers=superuser_token_headers)
    actual = resp.json()
    assert resp.status_code == status.HTTP_200_OK
    assert expected == actual


def test_get_unauthenticated_user(client: TestClient):
    expected = {"detail": "Not authenticated"}
    resp = client.get("/users/me")
    actual = resp.json()
    assert resp.status_code == status.HTTP_401_UNAUTHORIZED
    assert expected == actual


def test_set_user_as_inactive_with_superuser(
    client: TestClient, db: Session, superuser_token_headers: Dict[str, str]
):
    user_id = 5
    email = "jen@example.com"
    full_name = "Jen Doe"
    password = "fake_pass_123"
    data = {"is_active": False}
    expected = {
        "email": "jen@example.com",
        "full_name": "Jen Doe",
        "is_active": False,
        "is_superuser": False,
        "id": 5,
    }

    user_in = schemas.UserCreate(email=email, full_name=full_name, password=password)
    crud.create_user(db, user_in)
    resp = client.put(f"/users/{user_id}", headers=superuser_token_headers, json=data)
    actual = resp.json()
    assert resp.status_code == status.HTTP_200_OK
    assert expected == actual


def test_get_inactive_user(client: TestClient, db: Session):
    email = "allen@example.com"
    full_name = "Allen Doe"
    password = "fake_pass_123"
    expected = {"detail": "Inactive user"}

    user_create_in = schemas.UserCreate(
        email=email, full_name=full_name, password=password
    )
    user_create = crud.create_user(db, user_create_in)

    user_update_in = schemas.UserUpdate(is_active=False)
    crud.update_user(db, db_obj=user_create, obj_in=user_update_in)

    user_token_headers = authentication_token_from_email(
        client=client, db=db, email=email, password=password, full_name=full_name
    )
    resp = client.get("/users/me", headers=user_token_headers)
    actual = resp.json()
    assert resp.status_code == status.HTTP_400_BAD_REQUEST
    assert expected == actual
