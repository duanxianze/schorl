import psycopg2
# from parser_html import ParseHTML
DB_NAME = "sf_development"
USER = "Ru"
PASSWORD = ""
conn = psycopg2.connect("dbname={0} user={1} password={2}".format(DB_NAME, USER, PASSWORD))
cur = conn.cursor()

class QueryDB:
    def __init__(self,name):
        self.name = name
        self.start_url = None
        self.url = []

    def run(self):
        if self.name[1].strip()=='':
            self.start_url = 'https://scholar.google.com/scholar?start=0&q='+self.name[0].strip()+'+'+self.name[2].strip()+'&hl=en&as_sdt=0,5'
        else:
            self.start_url = 'https://scholar.google.com/scholar?start=0&q='+self.name[0].strip()+'+'+self.name[1].strip()+'+'+self.name[2].strip()+'&hl=en&as_sdt=0,5'

        return self.start_url

    def page(self):
        pass

cur.execute("select first_name, middle_name, last_name from scholars where id >=1000")
names =  [n for n in cur.fetchall()]

for name in names:
    query = QueryDB(name)
    query.run()
    print(name)
    print(query.start_url)
    query.page()
