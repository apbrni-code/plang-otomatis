import os
from sqlalchemy import text
from api.database import engine

def drop_leftover_tables():
    print("Menghapus tabel sisa dari skema lama...")
    
    statements = [
        'DROP TABLE IF EXISTS users CASCADE;',
        'DROP TABLE IF EXISTS log_akses CASCADE;',
        'DROP TABLE IF EXISTS personel CASCADE;',
        'DROP TABLE IF EXISTS kendaraan CASCADE;',
        'DROP TABLE IF EXISTS admin CASCADE;',
        'DROP TABLE IF EXISTS logakses CASCADE;',
    ]
    
    with engine.begin() as conn:
        for stmt in statements:
            conn.execute(text(stmt))
            
    print("Selesai menghapus tabel-tabel sisa!")

if __name__ == "__main__":
    drop_leftover_tables()
