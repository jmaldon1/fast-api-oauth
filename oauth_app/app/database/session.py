import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


def get_sqlalchemy_url():
    environment = os.getenv("ENVIRONMENT", "TEST")
    user = os.getenv("POSTGRES_USER", "postgres")
    password = os.getenv("POSTGRES_PASS", "")
    server = os.getenv("POSTGRES_SERVER", "localhost")
    db = os.getenv("POSTGRES_DB", "db")
    dev_db_port = os.environ["POSTGRES_DEV_PORT"]
    test_db_port = os.environ["POSTGRES_TEST_PORT"]
    port = dev_db_port if environment == "DEV" else test_db_port
    return f"postgresql://{user}:{password}@{server}:{port}/{db}"


SQLALCHEMY_DATABASE_URL = get_sqlalchemy_url()

engine = create_engine(SQLALCHEMY_DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
