from django.shortcuts import render
from pymongo import MongoClient
from urlparse import urlparse, parse_qs
from django.core.paginator import Paginator

mongodb_server = "127.0.0.1"
COUNT_PER_PAGE = 20

def getclient():
	return MongoClient(mongodb_server, 27017)

def index(request):
	qs = parse_qs(request.META['QUERY_STRING']) 
	page_no = int(GetQueryParam(qs, 'page', 1))
	
	client = getclient()
	order_system_db = client.order_system
	orders = order_system_db.orders
	
	p = Paginator(orders.find(), COUNT_PER_PAGE)
	page = p.page(page_no)
	orders = []
	for order in page.object_list:
		order['DDate'] = order['DDate'][0:order['DDate'].find(' ')]
		order['DComeDate'] = order['DComeDate'][0:order['DComeDate'].find(' ')]
		orders.append(order)
	page.object_list = orders
	print len(page.object_list)
	return render(request, 'order/index.html', 
				 {'page': page,
				  'pagination_required': p.num_pages > 1,})
	
	
	
def IsNotNullOrEmpty(value):
    return value is not None and len(value) > 0
 
def GetQueryParam(qs, name, default):
	return qs.get(name,[default])[0]
