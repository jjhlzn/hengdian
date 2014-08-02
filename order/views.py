from django.shortcuts import render
from pymongo import MongoClient
from django.core.paginator import Paginator

mongodb_server = "127.0.0.1"
COUNT_PER_PAGE = 20

def getclient():
	return MongoClient(mongodb_server, 27017)

def index(request):
	client = getclient()
	order_system_db = client.order_system
	orders = order_system_db.orders
	print orders.count()
	
	p = Paginator(orders.find(), COUNT_PER_PAGE)
	page = p.page(1)
	return render(request, 'order/orders.html', {'page': page})
	
	
	
