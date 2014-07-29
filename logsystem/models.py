from django.db import models

# Create your models here.
class OrderSystemLogRecord(models.Model):
	time = models.CharField(max_length=200)
	thread = models.CharField(max_length=500)
	level = models.CharField(max_length=500)
	clazz = models.CharField(max_length=500)
	content = models.CharField(max_length=4000)
