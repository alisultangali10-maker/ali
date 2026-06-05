import sqlite3
import os

def upgrade():
    db_path = 'C:\\Users\\user\\proekt\\news_kz.db'
    if not os.path.exists(db_path):
        print(f"Error: Database not found at {db_path}")
        return

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("Starting AI Migration...")
        
        # Add summary fields
        try:
            cursor.execute("ALTER TABLE news ADD COLUMN summary_ru TEXT;")
            print("Added summary_ru")
        except sqlite3.OperationalError:
            print("summary_ru already exists")

        try:
            cursor.execute("ALTER TABLE news ADD COLUMN summary_kk TEXT;")
            print("Added summary_kk")
        except sqlite3.OperationalError:
            print("summary_kk already exists")

        try:
            cursor.execute("ALTER TABLE news ADD COLUMN summary_en TEXT;")
            print("Added summary_en")
        except sqlite3.OperationalError:
            print("summary_en already exists")

        conn.commit()
        print("AI Migration successful")
    except Exception as e:
        print(f"Error during migration: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    upgrade()
