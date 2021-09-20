import os
from pathlib import Path
from typing import Union

from sqlalchemy.orm import Session
from alembic.config import Config as AlembicConfig
from alembic import command

from oauth_app.app import crud
from oauth_app.app import schemas


def migrate_db(root_dir: Union[str, Path] = ".") -> None:
    """Migrate (commit) the database revisions to the database.

    Args:
        root_dir (Union[str, Path]): Root directory of this project, needed in order to find the `alembic.ini` file.
    """
    alembic_cfg = AlembicConfig(os.path.join(root_dir, "alembic.ini"))
    command.upgrade(alembic_cfg, "head")


def create_superuser(db: Session) -> None:
    """Create a superuser that has the ability to set other users as inactive.

    Args:
        db (Session): Database session.
    """
    superuser_email = os.environ["SUPERUSER_EMAIL"]
    superuser_pass = os.environ["SUPERUSER_PASS"]
    user = crud.get_user_by_email(db, email=superuser_email)
    if not user:
        print("Creating Superuser.")
        user_in = schemas.UserCreate(
            email=superuser_email,
            password=superuser_pass,
            is_superuser=True,
        )
        user = crud.create_user(db, user_in)
    else:
        print("Superuser already exists.")
