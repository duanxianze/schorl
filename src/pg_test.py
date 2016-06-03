import psycopg2
conn = psycopg2.connect(dbname="sf_development", user="gao", password="gaotongfei13")
cur = conn.cursor()
cur.execute("select id from scholars where id>=3000 and id <=7000")
print(cur.fetchall())
