from django.shortcuts import render
from urlparse import urlparse, parse_qs
from logsystem.models import *
import datetime
from django.db import connection
from django.core.paginator import Paginator

CounterPerPage = 100

def index(request):
	qs = parse_qs(request.META['QUERY_STRING']) 
	day =  qs.get('date',[datetime.datetime.now().strftime("%Y-%m-%d")])[0] 
	page_no = int(qs.get('page',[1])[0])
	start_time = qs.get('start_time',[''])[0]
	end_time = qs.get('end_time',[''])[0]
	search_content = unicode(qs.get('search_content',[''])[0], 'UTF-8')
	time_from_now = qs.get('time_from_now',[''])[0]
	if (IsNotNullOrEmpty(time_from_now)):
		start_time = (datetime.datetime.now() + 
							datetime.timedelta(seconds=-int(time_from_now))).strftime("%H:%M:%S")
	
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
	p = Paginator(records, CounterPerPage)
	page = p.page(page_no)
	
	return render(request, 
				  "logsystem/index.html", 
				  {'page': page,
				   'pagination_required': p.num_pages > 1,
				   'date': day,
				   'start_time': start_time,
				   'end_time': end_time,
				   'search_content': search_content});

def IsNotNullOrEmpty(value):
    return value is not None and len(value) > 0

