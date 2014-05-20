from django.shortcuts import render
from lottery.models import Question,LotteryRecord,Prize
from urlparse import urlparse, parse_qs
import random

# Create your views here.
def index(request):
	return render(request, 'lottery/choujiang.html', {})

def choujiang_step(request):
	#query string map
	qs_map = parse_qs(request.META['QUERY_STRING']) 
	print qs_map
	if qs_map.get('name') is None or qs_map.get('mobile') is None:
		return render(request, 'lottery/choujiang.html', {})
	question_count = 2
	questions = Question.objects.all()[:question_count]
	question_map = dict(zip(range(1,question_count+1),questions))
	print question_map
	context = {'question_map': question_map,
			   'name': qs_map['name'][0],
			   'mobile': qs_map['mobile'][0],
			   'question_count': question_count}
	#for ques in questions:
	#	context
	#print seq_map[questions[0]]
	return render(request, 'lottery/choujiang_step.html', context)
	
def choujiang_handle(request):
	record = handle_lottery(request)
	if record.has_prize():
		return render(request, 'lottery/choujiang_result_yes.html', {})
	else:
		return render(request, 'lottery/choujiang_result_no.html', {})
	
#def choujiang_result_yes(request):
#	return render(request, 'lottery/choujiang_result_yes.html', {})

#def choujiang_result_no(request):
#	return render(request, 'lottery/choujiang_result_no.html', {})


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
	number = random.randint(1, 10)
	if number % 2 == 1:
		prize_list = Prize.objects.all()
		prize_index = random.randint(1,len(prize_list))-1
		prize = prize_list[prize_index]
		record = LotteryRecord()
		record.prize_name = prize.name
		print record.prize_name
		return record
	else:
		record = LotteryRecord()
		record.prize_name = ''
		print record.prize_name
		return record
		
	