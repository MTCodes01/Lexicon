"""
Database migration script to add password reset fields to users table.
"""
import os
import sys
from sqlalchemy import create_engine, text

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from api.config import settings

def migrate():
    """Add reset_token and reset_token_expires columns to users table."""
    engine = create_engine(settings.DATABASE_URL)
    
    with engine.connect() as conn:
        # Check if columns already exist
        result = conn.execute(text("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'users' 
            AND column_name IN ('reset_token', 'reset_token_expires')
        """))
        existing_columns = [row[0] for row in result]
        
        # Add reset_token if it doesn't exist
        if 'reset_token' not in existing_columns:
            conn.execute(text("ALTER TABLE users ADD COLUMN reset_token VARCHAR(255)"))
            print("✓ Added reset_token column")
        else:
            print("⊘ reset_token column already exists")
        
        # Add reset_token_expires if it doesn't exist
        if 'reset_token_expires' not in existing_columns:
            conn.execute(text("ALTER TABLE users ADD COLUMN reset_token_expires TIMESTAMP"))
            print("✓ Added reset_token_expires column")
        else:
            print("⊘ reset_token_expires column already exists")
        
        conn.commit()
        print("✅ Migration completed successfully!")

if __name__ == "__main__":
    migrate()
