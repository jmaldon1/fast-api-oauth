"""Initialize the database with migrations and a superuser
"""
from dotenv import load_dotenv

load_dotenv()
from oauth_app.app.database.init_db import migrate_db, create_superuser
from oauth_app.app.database.session import SessionLocal

if __name__ == "__main__":
    migrate_db()
    db = SessionLocal()
    create_superuser(db)
