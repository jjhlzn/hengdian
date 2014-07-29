from django.contrib import admin
from logsystem.models import *
# Register your models here.
class OrderSystemLogRecordAdmin(admin.ModelAdmin):
	list_display = ('time','thread', 'level', 'clazz', 'content')
	search_fields = ('time','thread', 'level', 'clazz', 'content')
	
admin.site.register(OrderSystemLogRecord,OrderSystemLogRecordAdmin);