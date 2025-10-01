import os
from app import db, User, ListenerApplication, ChatMessage, MoodEntry, JournalEntry, Habit, HabitEntry, app
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError

# Path to your old SQLite database
SQLITE_DB_PATH = os.path.join(os.path.dirname(__file__), 'instance', 'safe_space.db')
SQLITE_URI = f'sqlite:///{SQLITE_DB_PATH}'

# PostgreSQL URI (already set in app.py)
POSTGRES_URI = app.config['SQLALCHEMY_DATABASE_URI']

# Create engine and session for SQLite
sqlite_engine = create_engine(SQLITE_URI)
SQLiteSession = sessionmaker(bind=sqlite_engine)
sqlite_session = SQLiteSession()

def copy_table(Model, postgres_session):
    print(f"Migrating {Model.__tablename__}...")
    rows = sqlite_session.query(Model).all()
    for row in rows:
        # Create a new instance for PostgreSQL
        data = {c.name: getattr(row, c.name) for c in Model.__table__.columns}
        obj = Model(**data)
        postgres_session.merge(obj)  # merge to handle PK conflicts
    try:
        postgres_session.commit()
        print(f"{Model.__tablename__}: {len(rows)} rows migrated.")
    except IntegrityError as e:
        postgres_session.rollback()
        print(f"Error migrating {Model.__tablename__}: {e}")

if __name__ == "__main__":
    with app.app_context():
        PostgresSession = sessionmaker(bind=db.engine)
        postgres_session = PostgresSession()
        # Order matters for foreign keys
        copy_table(User, postgres_session)
        copy_table(ListenerApplication, postgres_session)
        copy_table(ChatMessage, postgres_session)
        copy_table(MoodEntry, postgres_session)
        copy_table(JournalEntry, postgres_session)
        copy_table(Habit, postgres_session)
        copy_table(HabitEntry, postgres_session)
        print("Migration complete!")
