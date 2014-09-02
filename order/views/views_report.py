# coding:UTF-8

from datetime import timedelta, date
from django.shortcuts import render
from django.http import HttpResponse
from urlparse import urlparse, parse_qs
from ..httputils import *
from ..dbutils import  *
import json

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

def order_statistic(request):
    return render(request, 'order/order_statistic.html', {})

def order_statistic_json(request):
    qs = parse_qs(request.META['QUERY_STRING'])
    time_unit = get_query_param(qs, 'time_unit', 'day')
    time_scale = get_query_param(qs, 'time_scale', 'oneyear')
    indicator = get_query_param(qs, 'indicator', 'people')
    params = {'time_scale': time_scale, 'time_unit': time_unit, 'indicator': indicator}
    context = _order_statistic(time_scale, time_unit)
    context['data0'] = [int(data[indicator]) for data in context['data0']]
    context['data1'] = [int(data[indicator]) for data in context['data1']]
    context['params'] = params
    response_data = {}
    response_data['data'] = context
    response_data['status'] = 0
    response_data['message'] = 'success'
    return HttpResponse(json.dumps(response_data), content_type="application/json")

def _order_statistic(time_scale, time_unit):
    dataset_2014 = _get_order_data('2014', time_scale, time_unit)
    dataset_2013 = _get_order_data('2013', time_scale, time_unit)
    if time_unit == 'day':
        x_lables = [x['order_date'][5:] for x in dataset_2013]
        if time_scale == 'oneyear' or time_scale == 'halfyear':
            pointDot = False
        else:
            pointDot = True
    else:
        x_lables = [str(x['_month']) + u'月' for x in dataset_2013]
        pointDot = True
    return {"data0": dataset_2014, "data1": dataset_2013,  'x_labels': x_lables, 'pointDot': pointDot}

def _get_order_data(year, time_scale, time_unit):
    if time_scale == '30days':
        today = date.today()
        days = timedelta(days=30)
        start_date = (today-days).strftime('%m-%d')
        end_date = today.strftime('%m-%d')
    elif time_scale == '3months':
        today = date.today()
        days = timedelta(days=90)
        start_date = (today-days).strftime('%m-%d')
        end_date = today.strftime('%m-%d')
    elif time_scale == 'halfyear':
        today = date.today()
        days = timedelta(days=181)
        start_date = (today-days).strftime('%m-%d')
        end_date = today.strftime('%m-%d')
    else:
        start_date = '1-1'
        end_date = '12-31'
    start_date = year +'-' + start_date
    end_date = year+'-' + end_date
    print start_date
    print end_date
    if time_unit == 'month':
        sql = """select _month, SUM(success_order_count) as success_order_count, SUM(people_count) as people_count, SUM(total_money) as total_money from (
              select MONTH(order_date) as _month, success_order_count, people_count, total_money
              from report.dbo.t_ordersystem_dailyorder where order_date >= '%s' and order_date <= '%s' ) as a group by _month"""
    else:
        sql = "select * from report.dbo.t_ordersystem_dailyorder where order_date >= '%s' and order_date <= '%s' order by order_date"
    sql = sql % (start_date, end_date)
    return get_rows_from_orders(sql)



