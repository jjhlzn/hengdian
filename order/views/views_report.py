# coding:UTF-8

from django.shortcuts import render
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
    sql = "select * from report.dbo.t_ordersystem_dailyorder where order_date >= '2014-4-18' order by order_date"
    rows = get_rows_from_orders(sql)
    #top 10 comedate
    sql = "select top 10 * from report.dbo.t_ordersystem_dailyorder where order_date >= '2014-4-18' order by success_order_count desc"
    top10_days = get_rows_from_orders(sql)
    return render(request, 'order/order_statistic.html', {"data": rows, "top10_days": top10_days})


