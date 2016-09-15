import os,psycopg2

def new_db_conn():
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
    return conn


CONN = new_db_conn()


def new_db_cursor(new_conn=True):
    if new_conn:
        conn = new_db_conn()
    else:
        conn = CONN
    return conn.cursor()


if __name__=="__main__":
    import time
    for i in range(10):

        conn = new_db_conn()
        cur = conn.cursor()
        print(conn,cur)
        #time.sleep(2)
        #conn.close()
        cur.close()
        print(new_db_cur())
        print('------------')