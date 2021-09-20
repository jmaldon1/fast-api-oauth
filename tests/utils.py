import time
import timeit
import subprocess
from typing import Union, Callable, List, Dict, Optional

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from oauth_app.app import crud
from oauth_app.app import schemas


def wait_until_responsive(
    check_func: Callable[[], bool],
    timeout: int = 30,
    pause: Union[int, float] = 0.1,
    clock=timeit.default_timer,
) -> None:
    """Wait until a service is responsive."""

    num_successful_connections = 0
    ref = clock()
    now = ref
    while (now - ref) < timeout:
        if check_func():
            num_successful_connections += 1
            if num_successful_connections == 3:
                return
        time.sleep(pause)
        now = clock()

    raise RuntimeError("Timeout reached while waiting on service!")


def is_process_responsive(cmd: List[str]) -> bool:
    """The command should be one that fails (non-0 exit code) if the process isn't responsive
    and passes (0 exit code) when the process is responsive.

    Args:
        cmd (List[str]): Command to check responsiveness

    Returns:
        bool: If the process being checked is responsive.
    """
    try:
        subprocess.check_output(cmd, stderr=subprocess.DEVNULL)
    except subprocess.CalledProcessError:
        return False

    return True


def user_authentication_headers(
    *, client: TestClient, email: str, password: str
) -> Dict[str, str]:
    data = {"username": email, "password": password}

    r = client.post("/token", data=data)
    response = r.json()
    auth_token = response["access_token"]
    headers = {"Authorization": f"Bearer {auth_token}"}
    return headers


def authentication_token_from_email(
    *,
    client: TestClient,
    db: Session,
    email: str,
    password: str,
    full_name: Optional[str] = None,
) -> Dict[str, str]:
    """
    Return a valid token for the user with given email.
    If the user doesn't exist it is created first.
    """
    user = crud.get_user_by_email(db, email=email)
    if not user:
        user_in_create = schemas.UserCreate(
            email=email, full_name=full_name, password=password
        )
        crud.create_user(db, user_in_create)

    return user_authentication_headers(client=client, email=email, password=password)
