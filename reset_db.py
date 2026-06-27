import os
from sqlalchemy import text
from api.database import engine

def execute_init_sql():
    sql_file = os.path.join(os.path.dirname(__file__), "database", "init.sql")
    
    with open(sql_file, "r") as f:
        sql_script = f.read()
        
    print("Mengeksekusi init.sql (DROP and CREATE CASCADE)...")
    
    with engine.begin() as conn:
        # Menghapus komentar dan memisahkan statement berdasarkan titik koma
        statements = [s.strip() for s in sql_script.split(';') if s.strip()]
        for stmt in statements:
            conn.execute(text(stmt))
            
    print("Database berhasil di-reset sesuai dengan init.sql!")

if __name__ == "__main__":
    execute_init_sql()
