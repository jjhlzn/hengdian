#coding:UTF-8
from __future__ import division
from django.shortcuts import render
from lottery.models import Question,LotteryRecord,Prize,PrizeConfiguration,Coupon,QuestionCode
from urlparse import urlparse, parse_qs
import random
import datetime
from django.utils import timezone
import string
from django.http import HttpResponseRedirect
from django.db.models import Q
import json
import urllib2
import threading
from django.db.models import Count

LOCK = threading.RLock()

#中奖概率
WIN_PRIZE_PROB = 0.5
#同一天抽中奖最多
MAX_WIN_PRIZE_CNT = 6
IS_SEND_MSG = True

def get_latest_lottery_records():
	has_prize_records = LotteryRecord.objects.filter(~Q(prize_name = '')).order_by('-lottery_time')[:10]
	for record in has_prize_records:
		record.mobile = record.mobile[:3]+'****'+record.mobile[7:]
	return has_prize_records


def index(request):
	qs = parse_qs(request.META['QUERY_STRING']) 
	return render(request, get_html_template(request,'lottery/choujiang.html'), {'has_prize_records':get_latest_lottery_records(),
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
				   'name': '',
				   'mobile': ''}
		return render(request, get_html_template(request,'lottery/choujiang.html'), context)
	questions = Question.objects.all()[(next_level-1) * question_count : next_level * question_count]
	question_map = dict(zip(range(1,question_count+1),questions))
	#生成问题码
	qc = QuestionCode()
	qc.code = id_generator()
	qc.time = datetime.datetime.now()
	qc.save()
	#print question_map
	context = {'question_map': question_map,
			   'name': name,
			   'mobile': mobile,
			   'question_count': question_count,
			   'next_level': next_level,
			   'errmsg': errmsg,
			   'question_code':qc.code}
	return render(request, get_html_template(request,'lottery/choujiang_step.html'), context)


def choujiang_handle(request):
	qs = parse_qs(request.META['QUERY_STRING']) 
	if qs.get('name') is None or qs.get('mobile') is None or qs.get('next_level') is None or qs.get('questioncode') is None:
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
		return render(request, get_html_template(request,'lottery/choujiang.html'), context)
	#检查问题码
	qc = (QuestionCode.objects.filter(code=qs['questioncode'][0],status=True)[:1] or [None])[0]
	if qc is None:
		return HttpResponseRedirect('/lottery/choujiang_step/?name='+qs['name'][0]+'&mobile='+qs['mobile'][0])
	qc.status = False
	qc.save()
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
		
				   
	   
		if lottery_record.has_prize():  
			msg = unicode("恭喜第",'UTF-8')+str(lottery_record.level)+unicode("关闯关成功！<br/> 恭喜你！抽中了一张【",'UTF-8')+lottery_record.prize_name+unicode("】，请在有效期内使用！赶快分享给你们的小伙伴吧！",'UTF-8')
		else:
			msg = unicode("恭喜第",'UTF-8')+str(lottery_record.level)+unicode("关闯关成功！<br/>本轮抽奖结果：奖品差一点就到手了，再接再励！",'UTF-8')
		context = {'name': qs['name'][0],
				   'mobile': qs['mobile'][0],
				   'prize_name': lottery_record.prize_name,
				   'msg': msg,
				   'id_nr': id_generator(9, string.digits),}
				   
		if lottery_record.level < 6:
			return render(request, get_html_template(request,'lottery/choujiang_result_yes.html'), context)
		else:
			if lottery_record.has_prize():  
				context['msg'] = unicode("抽中了一张【",'UTF-8')+lottery_record.prize_name+unicode("】，请在有效期内使用！赶快分享给你们的小伙伴吧！",'UTF-8')
			else:
				context['msg'] = unicode("奖品差一点就到手了，再接再励！",'UTF-8')
			return render(request, get_html_template(request,'lottery/choujiang_result_no.html'), context)
			
			
def choujiang_search(request):
	qs = parse_qs(request.META['QUERY_STRING']) 
	if qs.get('name') is None or qs.get('mobile') is None:
		has_prize_records = []
	else:
		has_prize_records = LotteryRecord.objects.filter(username=qs['name'][0],
														 mobile=qs['mobile'][0]).filter(~Q(prize_name = ''))
	for record in has_prize_records:
		if unicode('套餐抵金券','UTF-8') in record.prize_name:
			coupon = (Coupon.objects.filter(lotteryRecord=record)[0:1] or [None])[0]
			if coupon is not None:
				record.prize_name = record.prize_name + '[' + coupon.code + ']'
	return render(request, get_html_template(request,'lottery/choujiang_search.html'), {'has_prize_records': has_prize_records})
	
def choujiang_stat(request):
	win_lottery_count =reduce(lambda x,y: x+y,map(lambda x: x.use_count,Prize.objects.all()))
	lottery_count = len(LotteryRecord.objects.all())
	win_rate = '%' + str(win_lottery_count / lottery_count * 100)
	today_win_lottery_count = len(LotteryRecord.objects.filter(lottery_time__startswith=datetime.datetime.now().date).filter(~Q(prize_name='')))
	
	today_lottery_count = len(LotteryRecord.objects.filter(lottery_time__startswith=datetime.datetime.now().date))
	
	
	today_ip_summary = LotteryRecord.objects.filter(lottery_time__startswith=datetime.datetime.now().date).values('ip').annotate(count=Count('ip')).order_by('-count')[:10]
	mobile_win_summary = LotteryRecord.objects.filter(lottery_time__startswith=datetime.datetime.now().date).values('mobile').annotate(count=Count('mobile')).order_by('-count')[:10]
	name_mobile_win_summary = LotteryRecord.objects.filter(lottery_time__startswith=datetime.datetime.now().date).values('mobile','username').annotate(count=Count('mobile')).order_by('-count')[:10]
	
	for x in mobile_win_summary:
		x['win_count'] = len(LotteryRecord.objects.filter(lottery_time__startswith=datetime.datetime.now().date,mobile=x['mobile']).filter(~Q(prize_name='')))
	for x in name_mobile_win_summary:
		x['win_count'] = len(LotteryRecord.objects.filter(lottery_time__startswith=datetime.datetime.now().date,mobile=x['mobile'],username=x['username']).filter(~Q(prize_name='')))
	
	#一致性检查
	win_lottery_count2 = reduce(lambda x,y: x+y, map(lambda x: x.use_count,PrizeConfiguration.objects.all()))
	
	context = {
		'set_win_rate':  '%' + str(WIN_PRIZE_PROB * 100 ),
		'win_lottery_count': str(win_lottery_count),
		'lottery_count': str(lottery_count),
		'win_rate': win_rate,
		'today_lottery_count': str(today_lottery_count),
		'today_win_lottery_count': str(today_win_lottery_count),
		'today_win_rate': '%' + str(today_win_lottery_count / today_lottery_count * 100),
		'today_ip_summary': today_ip_summary,
		'mobile_win_summary': mobile_win_summary,
		'name_mobile_win_summary': name_mobile_win_summary,
		'Prize_PrizeConf': win_lottery_count2 == win_lottery_count,
		
	}
	
	
	
	return render(request, 'lottery/choujiang_stat.html', context)
	
##################################################辅助函数################################################
#处理抽奖，该方法需要同步，已避免超出奖品数量
def handle_lottery_request(request):
	with LOCK:
		qs = parse_qs(request.META['QUERY_STRING']) 
		name = qs['name'][0]
		mobile = qs['mobile'][0]
		record = lottery(get_client_ip(request),name,mobile)
		#如果是优惠券，还需要挑选优惠券，并且发送该优惠券
		if len(record.prize_name) == 0:
			print 'NO PRIZE'
		else:
			print 'WIN PRIZE'
		if unicode('套餐抵金券','UTF-8') in record.prize_name:
			coupon = get_and_set_coupon(record.prize_name)
			coupon.lotteryRecord = record
			print "coupon.id = " + str(coupon.id)
			sms_content = (unicode(name,'UTF-8') + u'，您好，恭喜您抽中了一张' + record.prize_name + u'，优惠码为[' + coupon.code + u']。').encode('UTF-8')
			url = 'http://e.hengdianworld.com/sendsms.aspx?phone='+mobile+'&content='+sms_content+'&sc=hengdian86547211jjh'
			#print url
			if IS_SEND_MSG:
				js = json.load(urllib2.urlopen(url))
			else:
				js = {'status':0}
			if js['status'] == 0:
				coupon.has_send = 1
			coupon.save()
	return record
	
def get_html_template(request,name):
	#request.mobile = True
	if request.mobile:
		name = name[0:-5]+'_wap.html'
	return name;
	
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

#奖品分摊到每一天，每次抽奖20%中奖概率， 同一人通关1次,  同一人总体中奖次数6次，每天都是重新冲关的
def lottery(ip,name,mobile):
	record = LotteryRecord()
	record.username = name
	record.mobile = mobile
	record.ip = ip
	record.lottery_time = timezone.now()
	record.level = get_next_level(name,mobile)
	win_prize_cnt = len(LotteryRecord.objects.filter(username=name,mobile=mobile,lottery_time__startswith=datetime.datetime.now().date).filter(~Q(prize_name = '')))
	if win_prize_cnt > MAX_WIN_PRIZE_CNT:
		print 'WARN: '+mobile+' has win too many prizes'
		record.prize_name = ''
	else:
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
   
def id_generator(size=15, chars=string.ascii_uppercase + string.digits):
	return ''.join(random.choice(chars) for _ in range(size))
   
	
		
	