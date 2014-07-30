from django.shortcuts import render
from urlparse import urlparse, parse_qs
from logsystem.models import *
import datetime

# Create your views here.
def index(request):
	qs = parse_qs(request.META['QUERY_STRING']) 
	if qs['date'] is None:
		day = datetime.datetime.now().strftime("%Y-%m-%d")
	else:
		day = qs['date'][0]
	if qs['page'] is None:
		page = 1
	else 
		page = qs['page'][0]
	from_time = qs['from_time'][0]
	end_time = qs['end_time'][0]
	search_content = qs['search_content'][0]
	
	records = OrderSystemLogRecord.objects;
	if IsNotNull(from_time):
		the_time = day + " " + from_tiem
		records = records.filter(time__gte=the_time)
	if IsNotNull(end_time):
		the_time = day + " " + end_time
		records = records.filter(time__gte=the_time)
	
		
	OrderSystemLogRecord.objects.filter()
	
	return render(request, "logsystem/index.html", {});



def IsNotNull(value):
    return value is not None and len(value) > 0
