from django.db import models

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
	expire_date = models.DateTimeField()
	def __unicode__(self):
		return self.name

class LotteryRecord(models.Model):
	ip = models.CharField(max_length=100)
	username = models.CharField(max_length=100)
	mobile = models.CharField(max_length=100)
	lottery_time = models.DateTimeField()
	prize_name =  models.CharField(max_length=500,default='')
	def has_prize(self):
		return self.prize_name != ''