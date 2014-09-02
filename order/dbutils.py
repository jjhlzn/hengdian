import _mssql

server = '127.0.0.1'
user = 'sa'
password = '123456'

__author__ = 'jjh'

def get_connection():
    conn = _mssql.connect(server=server, user=user, password=password, database='hdbusiness', charset="utf8")
    return conn

def get_rows_from_orders(sql, parameter=[]):
    data = []
    conn = get_connection()
    conn.execute_query(sql, parameter)
    for row in conn:
        data.append(row)
    conn.close()
    return data


