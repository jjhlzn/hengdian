# coding:UTF-8

from datetime import timedelta, date
from django.shortcuts import render
from django.http import HttpResponse
from urlparse import urlparse, parse_qs
import json
from ..httputils import *
from ..dbutils import  *

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
