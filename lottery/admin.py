from django.contrib import admin
from lottery.models import Question, Prize, LotteryRecord,PrizeConfiguration,Coupon, LotteryConfiguration
from django.contrib.admin import DateFieldListFilter

class QuestionAdmin(admin.ModelAdmin):
	list_display = ('question','answer')
	ordering = ('id',)

class PrizeAdmin(admin.ModelAdmin):
	list_display = ('name','quantity','use_count')
	ordering = ('id',)

class CouponAdmin(admin.ModelAdmin):
	list_display = ('name','code','status')
	search_fields = ('name','code', 'status')

class LotteryRecordAdmin(admin.ModelAdmin):
	list_display = ('username','mobile','level','ip','format_lottery_time','prize_name','format_comedate','format_identity')
	search_fields = ('username','mobile', 'prize_name')
	list_filter = (
        ('lottery_time', DateFieldListFilter),
    )
	def format_lottery_time(self,obj):
		return obj.lottery_time.strftime('%Y-%m-%d, %H:%M:%S')
	def format_comedate(self,obj):
		if obj.comedate is None:
			return ''
		else:
			return obj.comedate.strftime('%Y-%m-%d')
	def format_identity(self,obj):
		if obj.identity is None:
			return ''
		else:
			return obj.identity
		

class PrizeConfigurationAdmin(admin.ModelAdmin):
	list_display = ('prize','lottery_date','count','use_count')
	def lottery_date(self,obj):
		return obj.date.strftime('%Y-%m-%d')
	list_filter = (
        ('date', DateFieldListFilter),
    )
	
class LotteryConfigurationAdmin(admin.ModelAdmin):
	list_display = ('type','string_value','int_value')
	search_fields = ('type','string_value','int_value')
	


admin.site.register(Question,QuestionAdmin)
admin.site.register(Prize,PrizeAdmin)
admin.site.register(LotteryRecord,LotteryRecordAdmin)
admin.site.register(PrizeConfiguration,PrizeConfigurationAdmin)
admin.site.register(Coupon,CouponAdmin)
admin.site.register(LotteryConfiguration,LotteryConfigurationAdmin);
