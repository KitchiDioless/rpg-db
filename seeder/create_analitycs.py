import os
import psycopg2

ANALYTIC_ROLE = os.getenv("ANALYTIC_ROLE")
DB_USER = os.getenv("DB_USER")

conn = psycopg2.connect(
    dbname="migrator",
    user="migrator",
    password="sosiska",
    host="db"
)

cur = conn.cursor()
SEED_COUNT = int(os.environ.get("SEED_COUNT", 10))

def create_analitycs():
    cur.execute("SELECT 1 FROM pg_roles WHERE rolname = 'analytic';")
    if not cur.fetchone():
        cur.execute("CREATE ROLE analytic NOLOGIN;")
        print("Role «analytic» created")
    else:
        print("Role «analytic» already exists")

    cur.execute("GRANT CONNECT ON DATABASE migrator TO analytic;")
    cur.execute("GRANT USAGE ON SCHEMA public TO analytic;")
    
    cur.execute("GRANT SELECT ON ALL TABLES IN SCHEMA public TO analytic;")
    
    analyst_names = os.getenv("ANALYST_NAMES", "")
    if analyst_names:
        cur.execute(f"""
            SELECT format('CREATE USER %I WITH PASSWORD %L IN ROLE analytic', 
                          user_name, 
                          user_name || '_123')
            FROM unnest(string_to_array(%s, ',')) AS user_name;
        """, (analyst_names,))
        
        for (sql,) in cur.fetchall():
            cur.execute(sql)
            print(f"Executed: {sql}")
    else:
        print("No analyst users to create (ANALYST_NAMES is empty)")

    conn.commit()


if os.environ.get("APP_ENV") == "dev":
    create_analitycs()
    

conn.commit()
cur.close()
conn.close()
