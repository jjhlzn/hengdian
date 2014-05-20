from django.shortcuts import render
from lottery.models import Question,LotteryRecord,Prize
from urlparse import urlparse, parse_qs
import random
import datetime
from django.http import HttpResponseRedirect
from django.db.models import Q


# Create your views here.
def index(request):
	has_prize_records = LotteryRecord.objects.filter(~Q(prize_name = '')).order_by('-lottery_time')[:10]
	for record in has_prize_records:
		record.mobile = record.mobile[:3]+'****'+record.mobile[7:]
	return render(request, 'lottery/choujiang.html', {'has_prize_records':has_prize_records})

def choujiang_step(request):
	qs = parse_qs(request.META['QUERY_STRING']) 
	if qs.get('name') is None or qs.get('mobile') is None:
		return render(request, 'lottery/choujiang.html', {})
	question_count = 2
	questions = Question.objects.all()[:question_count]
	question_map = dict(zip(range(1,question_count+1),questions))
	print question_map
	context = {'question_map': question_map,
			   'name': qs['name'][0],
			   'mobile': qs['mobile'][0],
			   'question_count': question_count}
	#for ques in questions:
	#	context
	#print seq_map[questions[0]]
	return render(request, 'lottery/choujiang_step.html', context)
	
def choujiang_handle(request):
	qs = parse_qs(request.META['QUERY_STRING']) 
	if qs.get('name') is None or qs.get('mobile') is None:
		return render(request, 'lottery/choujiang.html', {})
	record = handle_lottery(request)
	return HttpResponseRedirect("/lottery/choujiang_result/?id="+str(record.id)+'&name='+qs['name'][0]+'&mobile='+qs['mobile'][0])

def choujiang_result(request):
	qs = parse_qs(request.META['QUERY_STRING']) 
	if qs.get('id') is None or qs.get('name') is None or qs.get('mobile') is None:
		return render(request, 'lottery/choujiang.html', {})
	lottery_record = (LotteryRecord.objects.filter(id=qs['id'][0],
												   username=qs['name'][0],
												   mobile=qs['mobile'][0])
												   [:1] or [None])[0]
	if lottery_record == None: #no lottery record
		return render(request, 'lottery/choujiang.html', {})
	else:
		context = {'name': qs['name'][0],
				   'mobile': qs['mobile'][0],
				   'prize_name': lottery_record.prize_name}
		if lottery_record.has_prize():  
			return render(request, 'lottery/choujiang_result_yes.html', context)
		else:
			return render(request, 'lottery/choujiang_result_no.html', context)

#return LotteryRecord
def handle_lottery(request):
	#0. check the ip can lottery 
	#   check the user can lottery
	
	#1. check if today has any prize
	
	#2.1 if no, return
	#2.2 if yes, continue
	
	#3. lottery to win prize
	
	#4. check if win prize
	
	#5.1 if no, return
	#5.2 if yes, continue
	
	#6. lottery to get which prize
	
	#7. return prize
	record = LotteryRecord()
	qs = parse_qs(request.META['QUERY_STRING']) 
	record.username = qs['name'][0]
	record.mobile = qs['mobile'][0]
	record.ip = get_client_ip(request)
	record.lottery_time = datetime.datetime.now()
	
	#simply lottery handle
	number = random.randint(1, 10)
	if number % 2 == 1:
		prize_list = Prize.objects.all()
		prize_index = random.randint(1,len(prize_list))-1
		prize = prize_list[prize_index]
		record.prize_name = prize.name
	else:
		record.prize_name = ''
	record.save()
	return record

def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip
		
	