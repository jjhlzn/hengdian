#coding:UTF-8

from django.shortcuts import render
from pymongo import MongoClient
from urlparse import urlparse, parse_qs
from django.core.paginator import Paginator

mongodb_server = "127.0.0.1"
COUNT_PER_PAGE = 10

def getclient():
	return MongoClient(mongodb_server, 27017)

def index(request):
	qs = parse_qs(request.META['QUERY_STRING']) 
	page_no = int(GetQueryParam(qs, 'page', 1))
	search_content = GetQueryParam(qs, 'search_content')
	
	client = getclient()
	db = client.order_system
	
	#search_content may be in SellID, orderuser.DName, DProDescript
	if IsNotNullOrEmpty(search_content):
		#{"$text": {"$search": search_content}}
		orders = db.orders.find({"$and": [{"$or": [{"SellID": search_content}, \
										           {"DProDescript": {"$regex": search_content}}, \
										           {"visitoruserinfo.DName": search_content}, \
										           {"orderuser.DName": search_content}, \
										           {"orderuser.agent.DName": {"$regex": search_content}}, \
										           ]},   \
										  {"DDate": {"$gt": "2014-07-01"}}]})
		print orders.explain()
	else:
		orders = db.orders.find({"DDate": {"$gt": "2014-07-01"}})
		print orders.explain()
	p = Paginator(orders, COUNT_PER_PAGE)
	page = p.page(page_no)
	result_set = []
	for order in page.object_list:
		order['DDate'] = order['DDate'][0:order['DDate'].find(' ')]
		order['DComeDate'] = order['DComeDate'][0:order['DComeDate'].find(' ')]
		order['status_msg'] = GetStatusMsg(order)
		result_set.append(order)
	page.object_list = result_set
	print len(page.object_list)
	return render(request, 'order/orders3.html', 
				 {'orders': page,
				  'pagination_required': p.num_pages > 1,
				  'page': page,
				  'search_params': "search_content=%s" % search_content})
	
	
def IsNotNullOrEmpty(value):
    return value is not None and len(value) > 0
 
def GetQueryParam(qs, name, default=''):
	return qs.get(name,[default])[0]

order_status_dict = {}
order_status_dict['-7'] = u'未支付'
order_status_dict['-6'] = u'无效订单'
order_status_dict['-5'] = u'未支付'
order_status_dict['-4'] = u'未支付'
order_status_dict['-3'] = u'未审核'
order_status_dict['-1'] = u'已审核'
order_status_dict['0'] = u'预定成功'
order_status_dict['1'] = u'已使用'
order_status_dict['2'] = u'已过期'
order_status_dict['3'] = u'已取消'
order_status_dict['9'] = u'错误'
order_status_dict['4'] = u'预定成功'

def GetStatusMsg(order):
	if order_status_dict.has_key(order['Flag']):
		return order_status_dict[order['Flag']]
	else:
		return u'未知状态'

