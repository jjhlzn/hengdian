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
    by_month = get_query_param(qs, 'by_month', '')

    if by_month:
        context = _order_statistic_by_month(request)
    else:
        context = _order_statistic_by_day(request)
    return render(request, 'order/order_statistic.html', context)

def ticketorder_stat(request):
    sql = """select _year as theyear, SUM(paywhencome_order_count) as paywhencome, SUM(paywhenorder_order_count) as paywhenorder from (
             select YEAR(order_date) as _year, paywhencome_order_count, (success_order_count - paywhencome_order_count) as paywhenorder_order_count
             from  report.dbo.t_ordersystem_dailyorder_comedate where order_date >= '2013-1-1' ) as a group by _year order by _year desc"""
    paytype_datasets = get_rows_from_orders(sql)

    sql = """select theyear, SUM(singleticket_order_count) as single_order_count, sum(singleticket_people_number) as single_people_number,
            SUM(singleticket_money) as single_money, SUM(combineticket_order_count) as combine_order_count, sum(combineticket_people_number) as combine_people_number,
            SUM(combineticket_money) as combine_money, SUM(unionticket_order_count) as union_order_count, sum(unionticket_people_number) as union_people_number,
            SUM(unionticket_money) as union_money  from (
            select YEAR(comedate) as theyear, * from report.dbo.t_ticketsystem_network_ticketorder_type_dailyreport
            where comedate >= '2014-1-1') as a group by theyear"""
    tickettype_datasets = get_rows_from_orders(sql)
    context = {"paytype_datasets":paytype_datasets, "tickettype_datasets": tickettype_datasets}

    return render(request, 'order/ticketorder_stat.html', context)

def _order_statistic_by_day(request):
    sql = "select * from report.dbo.t_ordersystem_dailyorder where order_date >= '2013-1-1' and order_date <= '2013-12-31' order by order_date"
    dataset_2013 = get_rows_from_orders(sql)
    sql = "select * from report.dbo.t_ordersystem_dailyorder where order_date >= '2014-1-1' and order_date <= '2014-12-31' order by order_date"
    dataset_2014 = get_rows_from_orders(sql)
    x_lables = [x['order_date'][5:] for x in dataset_2013]
    return {"data0": dataset_2014, "data1": dataset_2013,  'x_labels': x_lables, 'show_point': 'false'}

def _order_statistic_by_month(request):
    sql = """select _month, SUM(success_order_count) as success_order_count, SUM(people_count) as people_count, SUM(total_money) as total_money from (
              select MONTH(order_date) as _month, success_order_count, people_count, total_money
              from report.dbo.t_ordersystem_dailyorder where order_date >= '2013-1-1' and order_date <= '2013-12-31' ) as a group by _month"""
    dataset_2013 = get_rows_from_orders(sql)
    sql = """select _month, SUM(success_order_count) as success_order_count, SUM(people_count) as people_count, SUM(total_money) as total_money from (
              select MONTH(order_date) as _month, success_order_count, people_count, total_money
              from report.dbo.t_ordersystem_dailyorder where order_date >= '2014-1-1' and order_date <= '2014-12-31' ) as a group by _month"""
    dataset_2014 = get_rows_from_orders(sql)
    x_lables = [str(x['_month']) + u'月' for x in dataset_2013]
    return  {"data0": dataset_2014, "data1": dataset_2013,  'x_labels': x_lables, 'show_point': 'true'}

def get_query_param(qs, name, default):
    return qs.get(name,[default])[0]

