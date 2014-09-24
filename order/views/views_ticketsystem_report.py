# coding:UTF-8
from __future__ import division
from datetime import timedelta, date
from django.shortcuts import render
from django.http import HttpResponse
from urlparse import urlparse, parse_qs
import json
from ..httputils import *
from ..dbutils import  *


def ts_order_stat(request):
     return render(request, 'order/ts_order_stat.html', {})

def order_statistic_json(request):
    qs = parse_qs(request.META['QUERY_STRING'])
    time_unit = get_query_param(qs, 'time_unit', 'day')
    time_scale = get_query_param(qs, 'time_scale', 'oneyear')
    indicator = get_query_param(qs, 'indicator', 'people')
    accumulative = get_query_param(qs, 'accumulative', '0')
    params = {'time_scale': time_scale, 'time_unit': time_unit, 'indicator': indicator, 'accumulative': accumulative}
    context = _order_statistic(time_scale, time_unit, accumulative)
    context['data0'] = [int(data[indicator]) for data in context['data0']]
    context['data1'] = [int(data[indicator]) for data in context['data1']]
    context['params'] = params
    response_data = {}
    response_data['data'] = context
    response_data['status'] = 0
    response_data['message'] = 'success'
    return HttpResponse(json.dumps(response_data), content_type="application/json")

def _order_statistic(time_scale, time_unit, accumulative):
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
    if accumulative == '1':
        for idx, point in enumerate(dataset_2013):
            if idx != 0:
                dataset_2013[idx]['people_count'] += dataset_2013[idx-1]['people_count']
                dataset_2013[idx]['success_order_count'] += dataset_2013[idx-1]['success_order_count']
                dataset_2013[idx]['total_money'] += dataset_2013[idx-1]['total_money']
        for idx, point in enumerate(dataset_2014):
            if idx != 0:
                dataset_2014[idx]['people_count'] += dataset_2014[idx-1]['people_count']
                dataset_2014[idx]['success_order_count'] += dataset_2014[idx-1]['success_order_count']
                dataset_2014[idx]['total_money'] += dataset_2014[idx-1]['total_money']
    if accumulative == '1' and time_scale == 'oneyear' and time_unit == 'day':
        dataset_2014['2014-12-31'] = 156000000
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
        sql = """select _month, SUM(success_order_number) as success_order_count, SUM(order_people_number) as people_count, SUM(order_money) as total_money from (
              select MONTH(date) as _month, success_order_number, order_people_number, order_money
              from report.dbo.t_ticketsystem_network_dailyreport_comedate where date >= '%s' and date <= '%s' ) as a group by _month"""
    else:
        sql = """select success_order_number as success_order_count, order_people_number as people_count, order_money as total_money, date as order_date from
                report.dbo.t_ticketsystem_network_dailyreport_comedate where date >= '%s' and date <= '%s' order by date"""
    sql = sql % (start_date, end_date)
    print sql
    return get_rows_from_orders(sql)

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

def network_order_area(request):
    return render(request, 'order/ts_network_order_area.html')


AREA_TYPE_PROVINCE = 'province'
AREA_TYPE_CITY = 'city'

def network_order_area_json(request):
    province_datasets = _network_order_area_json(request, AREA_TYPE_PROVINCE)
    city_datasets = _network_order_area_json(request, AREA_TYPE_CITY, 16)
    context = {'datasets': province_datasets[0], 'datasets_src': province_datasets[1], 'datasets1': city_datasets[0], 'datasets1_src': city_datasets[1]}
    response_data = {}
    response_data['data'] = context
    response_data['status'] = 0
    response_data['message'] = 'success'
    return HttpResponse(json.dumps(response_data), content_type="application/json")

def _network_order_area_json(request, area_type,  topN = 9):
    filed_name = 'province'
    if area_type == AREA_TYPE_CITY:
        filed_name = 'city'
    sql = """SELECT %s, COUNT(*) as order_count, SUM(DDjNumber) as people_count, cast(SUM(DAmount) as int) as total_money FROM (
            SELECT a.Sellid, DTel, a.DDjNumber, a.DAmount, (SELECT %s FROM report.dbo.t_phonenumber where phonenumber = SUBSTRING(DTel,0,8)) as %s
            FROM iccard14.dbo.v_tbdTravelOk a inner join iccard14.dbo.v_tbdTravelOkCustomer b on a.SellID = b.SellID
            WHERE a. Flag in (0,1) and
            exists(select * from iccard14.dbo.tbdGroupType b where a.DGroupType = b.DName and a.DGroupTypeAssort = b.sType and DGroupRoomType = '网络用房')
            and DComeDate >= '2014-1-1') as a
            GROUP BY %s
            order by total_money desc""" % (filed_name, filed_name, filed_name, filed_name)

    rows = get_rows_from_orders(sql)
    total = reduce(lambda x, y: x + y, map(lambda item: item['total_money'], rows) )
    for row in rows:
        row['percent'] = "{0:.3f}".format(row['total_money'] / total * 100) + '%'
        row['label'] = row[filed_name]
        row['value'] = row['total_money']
        if row['label'] is None:
            row['label'] = u'未知'

    colors = ['#659AC9', '#A0BFBE', '#ADC896', '#B58371', '#DA917A', '#BE98B7', '#8B814C', '#CD69C9', '#CDC673', '#EEE8CD',
              '#CD919E', '#C1CDC1', '#8B8878', '#7F7F7F', '#607B8B', '#4682B4', '#8C8C8C']
    datasets = []
    other = {filed_name: '其他', 'order_count': 0, 'people_count': 0, 'total_money': 0, 'color': colors[-1]}

    index = 1

    for row in rows:
        province = row[filed_name]
        if index >  topN:
            other['order_count'] += row['order_count']
            other['people_count'] += row['people_count']
            other['total_money'] += row['total_money']
        else:
            row['color'] = colors[index-1]
            datasets.append(row)
        index += 1
    datasets.append(other)
    datasets = map(lambda(item): {  \
                    'value':  int(item['total_money']), \
					'color':  item['color'], \
					'highlight': item['color'], \
					'label': item[filed_name] if  item[filed_name] is not None else u'未知'\
				 }, datasets)

    return [datasets, rows]


