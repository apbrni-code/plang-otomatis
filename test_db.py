import sys
import traceback
from sqlalchemy import text
from api.database import engine
from api import models

try:
    with engine.connect() as conn:
        result = conn.execute(text("SELECT 1"))
        print("Database connection successful:", result.scalar())
    
    # Also try to create tables
    models.Base.metadata.create_all(bind=engine)
    print("Tables created/verified successfully.")
except Exception as e:
    print("Error connecting to database:")
    traceback.print_exc()
    sys.exit(1)
