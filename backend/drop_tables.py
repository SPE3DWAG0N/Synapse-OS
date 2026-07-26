from app.database import engine, Base
import app.models

print("Dropping all tables...")
Base.metadata.drop_all(bind=engine)
print("Done.")
