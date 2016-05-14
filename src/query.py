import psycopg2

DB_NAME = "sf_development"
USER = "gao"
PASSWORD = "gaotongfei13"
conn = psycopg2.connect("dbname={0} user={1} password={2}".format(DB_NAME, USER, PASSWORD))
cur = conn.cursor()

class QueryDB:
    def __init__(self):
        cur.execute("select (first_name, middle_name, last_name) from scholars where id >= 1000")
        self.names = [n for n in cur.fetchall()]

    def run(self):
        print(self._names_list)

query = QueryDB()
query.run()

