import sqlite3

def upgrade():
    try:
        conn = sqlite3.connect('C:\\Users\\user\\proekt\\news_kz.db')
        cursor = conn.cursor()
        cursor.execute("ALTER TABLE news ADD COLUMN source_name VARCHAR(100);")
        cursor.execute("ALTER TABLE news ADD COLUMN original_url VARCHAR(500);")
        cursor.execute("CREATE UNIQUE INDEX ix_news_original_url ON news (original_url);")
        conn.commit()
        print("Migration successful")
    except Exception as e:
        print(f"Error during migration: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    upgrade()
