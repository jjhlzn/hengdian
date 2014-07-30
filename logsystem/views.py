from django.shortcuts import render
from urlparse import urlparse, parse_qs
from logsystem.models import *
import datetime
from django.db import connection

CounterPerPage = 100

def index(request):
	qs = parse_qs(request.META['QUERY_STRING']) 
	day =  qs.get('date',[datetime.datetime.now().strftime("%Y-%m-%d")])[0] 
	page = qs.get('page',[1])[0]
	start_time = qs.get('start_time',[None])[0]
	end_time = qs.get('end_time',[None])[0]
	search_content = qs.get('search_content',[None])[0]
	
	records = OrderSystemLogRecord.objects.all();
	
	if IsNotNullOrEmpty(start_time):
		the_time = day + " " + start_time
	else:
		the_time = day
	print the_time+"\n"
	records = records.filter(time__gte=the_time)
	
	if IsNotNullOrEmpty(end_time):
		the_time = day + " " + end_time + ",999"
		print the_time+"\n"
		records = records.filter(time__lte=the_time)
	
	
	if IsNotNullOrEmpty(search_content):
		print "search_content=["+search_content+"]\n" 
		records = records.filter(content__icontains=search_content) 
	records = records.order_by("time")
	records = records[(int(page) - 1) * CounterPerPage: int(page) * CounterPerPage]
	#print "--------------------------------------------------------------------\n"
	
	print records.query
	return render(request, "logsystem/index.html", {'records': records});

def IsNotNullOrEmpty(value):
    return value is not None and len(value) > 0

