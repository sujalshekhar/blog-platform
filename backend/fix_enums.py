from app.core.database import engine
from sqlalchemy import text

def run():
    with engine.connect().execution_options(isolation_level="AUTOCOMMIT") as conn:
        try:
            conn.execute(text("ALTER TYPE notification_type ADD VALUE 'FEATURE_REQUESTED'"))
            print("Added FEATURE_REQUESTED to notification_type")
        except Exception as e:
            print(f"notification_type: {e}")
            
        try:
            conn.execute(text("ALTER TYPE feature_status ADD VALUE 'COMPLETED'"))
            print("Added COMPLETED to feature_status")
        except Exception as e:
            print(f"feature_status: {e}")

if __name__ == "__main__":
    run()
