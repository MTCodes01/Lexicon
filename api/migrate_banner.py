import os
import sys
from sqlalchemy import create_engine, text

# Add parent directory to path to import config
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from api.config import settings

def migrate():
    """Add banner_url column to users table."""
    print("Migrating database...")
    
    engine = create_engine(settings.DATABASE_URL)
    
    try:
        with engine.connect() as conn:
            # Check if column exists
            result = conn.execute(text(
                "SELECT column_name FROM information_schema.columns "
                "WHERE table_name='users' AND column_name='banner_url'"
            ))
            
            if result.fetchone():
                print("Column 'banner_url' already exists.")
                return

            # Add column
            print("Adding 'banner_url' column to users table...")
            conn.execute(text("ALTER TABLE users ADD COLUMN banner_url VARCHAR(500)"))
            conn.commit()
            print("Migration successful!")
            
    except Exception as e:
        print(f"Migration failed: {e}")

if __name__ == "__main__":
    migrate()
