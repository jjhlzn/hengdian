from django.db import models
import datetime

# Create your models here.
class Question(models.Model):
	question = models.CharField(max_length=4000)
	option1 = models.CharField(max_length=500)
	option2 = models.CharField(max_length=500)
	option3 = models.CharField(max_length=500)
	answer = models.CharField(max_length=500)
	def __unicode__(self):
		return self.question
	
class Prize(models.Model):
	name = models.CharField(max_length=500)
	quantity =  models.IntegerField(default=0)
	expire_date = models.DateField()
	use_count = models.IntegerField(default=0)
	def __unicode__(self):
		return self.name
	

class PrizeConfiguration(models.Model):
	prize = models.ForeignKey(Prize)
	date = models.DateField()
	count = models.IntegerField(default=0)
	use_count = models.IntegerField(default=0)
	def remain_cnt(self):
		return self.count - self.use_count
	def __unicode__(self):
		return self.prize.name

class LotteryRecord(models.Model):
	ip = models.CharField(max_length=100)
	username = models.CharField(max_length=100)
	mobile = models.CharField(max_length=100)
	level = models.IntegerField(default=1)
	lottery_time = models.DateTimeField()
	prize_name =  models.CharField(max_length=500,default='')
	def has_prize(self):
		return self.prize_name != ''
	def __unicode__(self):
		return self.username + ',' + self.mobile + ','+self.prize_name
	
class Coupon(models.Model):
	name = models.CharField(max_length=100)
	code = models.CharField(max_length=100)
	status = models.BooleanField(default=False)
	has_send = models.BooleanField(default=False)
	lotteryRecord = models.ForeignKey(LotteryRecord,null=True,blank=True)
	def __unicode__(self):
		return self.name + ', ' + self.code

class QuestionCode(models.Model):
	code = models.CharField(max_length=100)
	status = models.BooleanField(default=True)
	time = models.DateTimeField()
	
class LotteryConfiguration(models.Model):
	type = models.CharField(max_length=500)
	string_value = models.CharField(max_length=500)
	int_value = models.IntegerField(default=0)
	
	