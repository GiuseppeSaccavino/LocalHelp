import sqlite3

OUTPUT_FILE = "db_dump.txt"

def create_table(DB_FILE):
    connection = sqlite3.connect(DB_FILE)
    with open('DB_create.sql') as f:
        connection.executescript(f.read())
    connection.commit()
    connection.close()

def insert_RPC(DB_FILE):
    connection = sqlite3.connect(DB_FILE)
    with open('insert_RPC.sql') as f:
        connection.executescript(f.read())
    connection.commit()
    connection.close()

def print_db(DB_FILE):
    connection = sqlite3.connect(DB_FILE)
    connection.execute("PRAGMA foreign_keys = ON")
    cur = connection.cursor()
    
    tables = ["utente", "locazione", "regioni", "province", "comuni", "post", "genere", "post_genere"]
    
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        for table in tables:
            f.write(f"\n--- {table.upper()} ---\n")
            cur.execute(f"SELECT * FROM {table}")
            rows = cur.fetchall()
            if rows:
                for row in rows:
                    f.write(f"{row}\n")
            else:
                f.write("Vuoto\n")
    
    connection.close()
    print(f"Tutto il contenuto del database è stato scritto in '{OUTPUT_FILE}'")
