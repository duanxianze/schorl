import os,psycopg2

def new_db_cursor():
    if os.name is 'nt':
        conn = psycopg2.connect(
            host = '45.32.11.113',
            port = 5432,
            dbname = "sf_development",
            user = "lyn",
            password = "tonylu716"
        )
    else:
        conn = psycopg2.connect(
            dbname = "sf_development",
            user = "lyn",
            password = "tonylu716"
        )
    conn.autocommit = True
    return conn.cursor()