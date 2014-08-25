# coding:UTF-8

from django.shortcuts import render
from urlparse import urlparse, parse_qs
import _mssql

server = '127.0.0.1'
user = 'sa'
password = '123456'

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

def order_statistic(request):
    qs = parse_qs(request.META['QUERY_STRING'])

    sql = "select * from report.dbo.t_ordersystem_dailyorder where order_date >= '2013-1-1' and order_date <= '2013-12-31' order by order_date"
    dataset_2013 = get_rows_from_orders(sql)
    sql = "select * from report.dbo.t_ordersystem_dailyorder where order_date >= '2014-1-1' and order_date <= '2014-12-31' order by order_date"
    dataset_2014 = get_rows_from_orders(sql)

    return render(request, 'order/order_statistic.html', {"data0": dataset_2014, "data1": dataset_2013})

def get_query_param(qs, name, default):
    return qs.get(name,[default])[0]

