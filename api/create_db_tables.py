from api.database import Base, engine
from api.core import models

print("Creating database tables...")
Base.metadata.create_all(bind=engine)
print("Database tables created successfully.")