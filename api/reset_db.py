from api.database import Base, engine, SessionLocal
from api.core import models  # Import models to ensure they are registered
from api.core.init_data import init_default_data

def reset_database():
    print("⚠️  Resetting database...")
    
    print("  🗑️  Dropping all tables...")
    Base.metadata.drop_all(bind=engine)
    
    print("  ✨ Creating all tables...")
    Base.metadata.create_all(bind=engine)
    
    print("  📝 Initializing default data...")
    db = SessionLocal()
    try:
        init_default_data(db)
    finally:
        db.close()
        
    print("✅ Database reset complete!")

if __name__ == "__main__":
    reset_database()
