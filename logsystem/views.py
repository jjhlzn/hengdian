from django.shortcuts import render
from urlparse import urlparse, parse_qs
from logsystem.models import *
import datetime
from django.db import connection
from django.core.paginator import Paginator
from django.db.models import Q

CounterPerPage = 100

def index(request):
	# parse query parameters
	qs = parse_qs(request.META['QUERY_STRING']) 
	day =  GetQueryParam(qs, 'date', 
				datetime.datetime.now().strftime("%Y-%m-%d")) 
	page_no = int(GetQueryParam(qs, 'page', 1))
	start_time = GetQueryParam(qs, 'start_time', '')
	end_time = GetQueryParam(qs, 'end_time', '')
	search_content = unicode(GetQueryParam(qs, 'search_content', ''), 'UTF-8')
	thread = GetQueryParam(qs, 'thread', '')
	time_from_now = GetQueryParam(qs, 'time_from_now', '')
	if (IsNotNullOrEmpty(time_from_now)):
		start_time = (datetime.datetime.now() + datetime.timedelta(seconds=-int(time_from_now))).strftime("%H:%M:%S")
	
	# search log record according to query parameters
	query = OrderSystemLogRecord.objects.all()
	
	if IsNotNullOrEmpty(start_time):
		the_time = day + " " + start_time
	else:
		the_time = day
	query = query.filter(time__gte=the_time)
	
	if IsNotNullOrEmpty(end_time):
		the_time = day + " " + end_time + ",999"
		query = query.filter(time__lte=the_time)
	
	if IsNotNullOrEmpty(thread):
		query = query.filter(thread=thread)
	
	if IsNotNullOrEmpty(search_content):
		query = query.filter(Q(content__icontains=search_content) 
									| Q(clazz__icontains=search_content)) 
	query = query.order_by("time")
	
	p = Paginator(query, CounterPerPage)
	page = p.page(page_no)
	
	#for a in query:
	#	1 + 1
	#print connection.queries
	
	return render(request, 
				  "logsystem/index.html", 
				  {'page': page,
				   'pagination_required': p.num_pages > 1,
				   'date': day,
				   'start_time': start_time,
				   'end_time': end_time,
				   'search_content': search_content,
				   'thread': thread},);

def IsNotNullOrEmpty(value):
    return value is not None and len(value) > 0
 
def GetQueryParam(qs, name, default):
	return qs.get(name,[default])[0]

