import os
import subprocess
from pathlib import Path
from typing import Union

import pytest
from _pytest.config import Config as PytestConfig
from sqlalchemy.orm import Session

from oauth_app.app.database.init_db import migrate_db, create_superuser

from tests.utils import is_process_responsive, wait_until_responsive


@pytest.fixture(scope="session", autouse=True)
def postgres_db(
    pytestconfig: PytestConfig, db: Session, set_superuser_env_vars: None
) -> None:
    """Start the Postgres docker service

    Args:
        pytestconfig (PytestConfig): Pytest config fixture.
    """
    root_dir = pytestconfig.rootdir
    docker_compose_path = os.path.join(root_dir, "docker-compose.yml")
    docker_compose_test_path = os.path.join(root_dir, "docker-compose.test.yml")
    postgres_user = os.environ["POSTGRES_USER"]
    postgres_db = os.environ["POSTGRES_DB"]
    container_name = "postgres-TEST"
    docker_cmd = ["docker", "exec", "-it", container_name]
    pg_responsive_cmd = docker_cmd + [
        "pg_isready",
        "-U",
        postgres_user,
        "-d",
        postgres_db,
    ]
    docker_compose_up_cmd = [
        "docker-compose",
        "-f",
        docker_compose_path,
        "-f",
        docker_compose_test_path,
        "up",
        "-d",
    ]
    docker_compose_rm_cmd = ["docker-compose", "rm", "-fsv"]

    subprocess.check_call(docker_compose_up_cmd)
    wait_until_responsive(lambda: is_process_responsive(pg_responsive_cmd))
    initialize_db(root_dir, db)
    yield  # Run tests
    subprocess.check_call(docker_compose_rm_cmd)


def initialize_db(root_dir: Union[str, Path], db: Session) -> None:
    migrate_db(root_dir)
    create_superuser(db)
