import os
from unittest import mock
from typing import Iterator, Dict

import pytest
from dotenv import load_dotenv

load_dotenv(".test.env")  # Export test env vars first to ensure they have priority
load_dotenv()

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from oauth_app.main import app

from tests.utils import authentication_token_from_email

# Fixtures
from tests.docker_services.postgres import postgres_db  # noqa


@pytest.fixture(scope="module")
def client() -> Iterator[TestClient]:
    with TestClient(app) as c:
        yield c


@pytest.fixture(scope="session")
def db() -> Iterator[Session]:
    from oauth_app.app.database.session import SessionLocal

    yield SessionLocal()


@pytest.fixture(scope="session")
def set_superuser_env_vars() -> Iterator[None]:
    """Set the test superuser login credentials."""
    env_vars = {"SUPERUSER_EMAIL": "admin@example.com", "SUPERUSER_PASS": "admin"}
    with mock.patch.dict(os.environ, env_vars):
        yield


@pytest.fixture
def superuser_token_headers(
    client: TestClient, db: Session
) -> Iterator[Dict[str, str]]:
    """Provides superuser token headers to allow for testing of URLs
    that are protected by superuser priveleges.
    """
    email = os.environ["SUPERUSER_EMAIL"]
    password = os.environ["SUPERUSER_PASS"]
    user_token_headers = authentication_token_from_email(
        client=client, db=db, email=email, password=password
    )
    return user_token_headers
