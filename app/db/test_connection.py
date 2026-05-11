from sqlalchemy import text

from app.db.session import SessionLocal


def test_database_connection():
    db = SessionLocal()

    try:
        result = db.execute(text("SELECT 1"))
        value = result.scalar()

        if value == 1:
            print("Database connection successful")
        else:
            print("Database connection failed")

    except Exception as error:
        print("Database connection error:")
        print(error)

    finally:
        db.close()


if __name__ == "__main__":
    test_database_connection()