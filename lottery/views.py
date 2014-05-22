#coding:UTF-8
from __future__ import division
from django.shortcuts import render
from lottery.models import Question,LotteryRecord,Prize,PrizeConfiguration,Coupon
from urlparse import urlparse, parse_qs
import random
import datetime
from django.utils import timezone

from django.http import HttpResponseRedirect
from django.db.models import Q
import json
import urllib2

def get_latest_lottery_records():
	has_prize_records = LotteryRecord.objects.filter(~Q(prize_name = '')).order_by('-lottery_time')[:10]
	for record in has_prize_records:
		record.mobile = record.mobile[:3]+'****'+record.mobile[7:]
	return has_prize_records

def index(request):
	qs = parse_qs(request.META['QUERY_STRING']) 
	return render(request, 'lottery/choujiang.html', {'has_prize_records':get_latest_lottery_records(),
													  'name': '' if qs.get('name') is None else qs['name'][0],
													  'mobile': '' if qs.get('mobile') is None else qs['mobile'][0]})

def choujiang_step(request):
	qs = parse_qs(request.META['QUERY_STRING']) 
	if qs.get('name') is None or qs.get('mobile') is None:
		return HttpResponseRedirect('/lottery/')
	name = qs['name'][0]
	mobile = qs['mobile'][0]
	errmsg = '' if qs.get('errmsg') is None else qs['errmsg'][0]
	print  "errmsg:" + errmsg
	#获取题目
	question_count = 10
	next_level = get_next_level(name,mobile)
	if next_level == 7:
		#该用户已经闯完关了
		context = {'errmsg': unicode('你今天已经完成闯关，请明天再来！','UTF-8'),
				   'has_prize_records':get_latest_lottery_records(),
				   'name': name,
				   'mobile': mobile}
		return render(request, 'lottery/choujiang.html', context)
	questions = Question.objects.all()[(next_level-1) * question_count : next_level * question_count]
	question_map = dict(zip(range(1,question_count+1),questions))
	print question_map
	context = {'question_map': question_map,
			   'name': name,
			   'mobile': mobile,
			   'question_count': question_count,
			   'next_level': next_level,
			   'errmsg': errmsg}
	return render(request, 'lottery/choujiang_step.html', context)
	
def choujiang_handle(request):
	qs = parse_qs(request.META['QUERY_STRING']) 
	if qs.get('name') is None or qs.get('mobile') is None or qs.get('next_level') is None:
		print 'required parameters have empty value'
		return HttpResponseRedirect('/lottery/')
	next_level = get_next_level(qs['name'][0],qs['mobile'][0])
	if qs['next_level'][0] <> str(next_level):
		print 'wrong next_level value, should be ' + str(next_level)+', but it is'+str(qs['next_level'][0])
		return HttpResponseRedirect('/lottery/choujiang_step/?name='+qs['name'][0]+'&mobile='+qs['mobile'][0]+'&errmsg='+'重新刷新题目')
	if next_level >= 7:
		#该用户已经闯完关了
		context = {'errmsg': unicode('你今天已经完成闯关，请明天再来！','UTF-8'),
				   'has_prize_records':get_latest_lottery_records()}
		return render(request, 'lottery/choujiang.html', context)
	record = handle_lottery_request(request)
	return HttpResponseRedirect("/lottery/choujiang_result/?id="+str(record.id)+'&name='+qs['name'][0]+'&mobile='+qs['mobile'][0])

def choujiang_result(request):
	qs = parse_qs(request.META['QUERY_STRING']) 
	if qs.get('id') is None or qs.get('name') is None or qs.get('mobile') is None:
		return HttpResponseRedirect('/lottery/')
	lottery_record = (LotteryRecord.objects.filter(id=qs['id'][0],
												   username=qs['name'][0],
												   mobile=qs['mobile'][0])
												   [:1] or [None])[0]
	if lottery_record == None: #no lottery record
		return HttpResponseRedirect('/lottery/')
	else:
		context = {'name': qs['name'][0],
				   'mobile': qs['mobile'][0],
				   'prize_name': lottery_record.prize_name}
		if lottery_record.has_prize():  
			return render(request, 'lottery/choujiang_result_yes.html', context)
		else:
			return render(request, 'lottery/choujiang_result_no.html', context)
			
def choujiang_search(request):
	qs = parse_qs(request.META['QUERY_STRING']) 
	if qs.get('name') is None or qs.get('mobile') is None:
		has_prize_records = []
	else:
		has_prize_records = LotteryRecord.objects.filter(username=qs['name'][0],
														 mobile=qs['mobile'][0]).filter(~Q(prize_name = ''))
	return render(request, 'lottery/choujiang_search.html', {'has_prize_records': has_prize_records})
	
	
##################################################辅助函数#####################################################################

#处理抽奖，该方法需要同步，已避免超出奖品数量
def handle_lottery_request(request):
	qs = parse_qs(request.META['QUERY_STRING']) 
	name = qs['name'][0]
	mobile = qs['mobile'][0]
	#奖品分摊到每一天，每次抽奖20%中奖概率， 同一人通关1次,  同一人总体中奖次数6次，每天都是重新冲关的
	MAX_WIN_PRIZE_CNT = 6
	win_prize_cnt = len(LotteryRecord.objects.filter(username=name,mobile=mobile).filter(~Q(prize_name = '')))
	if win_prize_cnt > MAX_WIN_PRIZE_CNT:
		#print name+','+mobile+' has win too many prizes'
		return HttpResponseRedirect('/lottery/')
	record = lottery(get_client_ip(request),name,mobile)
	#如果是优惠券，还需要挑选优惠券，并且发送该优惠券
	if unicode('套餐抵金券','UTF-8') in record.prize_name:
		coupon = get_and_set_coupon(record.prize_name)
		coupon.lottery_record = record
		#sms_content = record.prize_name.encode('UTF-8')
		#print sms_content
		sms_content = (unicode(name,'UTF-8') + u'，您好，恭喜您抽中了一张' + record.prize_name + u'，优惠码为[' + coupon.code + u']。').encode('UTF-8')
		url = 'http://e.hengdianworld.com/sendsms.aspx?phone='+mobile+'&content='+sms_content+'&sc=hengdian86547211jjh'
		#print url
		#js = json.load(urllib2.urlopen(url))
		js = {'status':0}
		print js
		if js['status'] == 0:
			coupon.has_send = 1
		coupon.save()
		
	return record

def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

#获取用户的闯关数
def get_next_level(name,mobile):
	max_record = (LotteryRecord.objects.filter(username=name,mobile=mobile,lottery_time__startswith=datetime.datetime.now().date).order_by('-level')[:1] or [None])[0]
	if max_record == None:
		return 1
	return max_record.level + 1

#检查当天是否还有奖品
def check_has_prize():
	prizes = filter(lambda x: x.quantity - x.use_count > 0, Prize.objects.all())
	if len(prizes) == 0:
		print "WARN: there isn't any prize at all"
		return False
	prize_configs = PrizeConfiguration.objects.filter(date=datetime.datetime.now().date)
	for prize_config in prize_configs:
		if prize_config.remain_cnt() > 0:
			#print prize_config.prize.name + ', ' + str(prize_config.remain_cnt()) 
			return True;
	print 'INFO:  there in no prize today'
	return False;

def lottery(ip,name,mobile):
	record = LotteryRecord()
	record.username = name
	record.mobile = mobile
	record.ip = ip
	record.lottery_time = timezone.now()
	record.level = get_next_level(name,mobile)
	if  check_has_prize():
		#奖品分摊到每一天，每次抽奖20%中奖概率， 同一人通关1次, 同一人总体中奖次数6次，每天都是重新冲关的
		if check_if_win() : #win prize
			#lottery prize
			prize_config = choose_prize()
			prize = prize_config.prize
			record.prize_name = prize.name
			prize_config.use_count = prize_config.use_count + 1
			prize_config.save()
			
			prize.use_count += 1
			prize.save()
			
		else:
			record.prize_name = ''
	else:
		record.prize_name = ''
	record.save()	
	return record
		
def check_if_win():
	#每次闯关的中奖概率
	WIN_PRIZE_PROB = 0.2
	choices = [[1,WIN_PRIZE_PROB],[0,1-WIN_PRIZE_PROB]]
	return weighted_choice(choices) == 1
	
def choose_prize():
	prize_configs = filter(lambda x: x.remain_cnt() > 0, PrizeConfiguration.objects.filter(date=datetime.datetime.now().date))
	cnt_list = map(lambda x: x.remain_cnt(), prize_configs)
	total_count = reduce(lambda x,y: x+y, cnt_list)
	choices = map(lambda x,y:[y,x/total_count],cnt_list,prize_configs)
	prize_config = weighted_choice(choices)
	return prize_config

#需要同步
def get_and_set_coupon(prize_name):
	coupons = Coupon.objects.filter(name=prize_name, status=False)
	#print 'Coupons:'
	#print coupons
	if len(coupons) == 0:
		raise Exception(prize_name+': there is no this type coupon')
	coupon = coupons[0]
	print 'get_and_set_coupon --------------'
	coupon.status = 1
	coupon.save()
	return coupon
	
def weighted_choice(choices):
   total = sum(w for c, w in choices)
   r = random.uniform(0, total)
   upto = 0
   for c, w in choices:
      if upto + w > r:
         return c
      upto += w
   assert False, "Shouldn't get here"
   
	
		
	