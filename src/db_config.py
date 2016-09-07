import os,psycopg2

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
cur = conn.cursor()
conn.autocommit = True