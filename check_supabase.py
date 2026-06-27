import os
from api.database import SessionLocal, engine
from api.models import Admin

def check_supabase():
    print(f"Connecting to: {engine.url}")
    db = SessionLocal()
    admins = db.query(Admin).all()
    print(f"Jumlah admin di database: {len(admins)}")
    for a in admins:
        print(f"- {a.namaadmin}")
    db.close()

if __name__ == "__main__":
    check_supabase()
