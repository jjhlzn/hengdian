from django.contrib import admin
from lottery.models import Question, Prize, LotteryRecord,PrizeConfiguration,Coupon
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
	list_display = ('username','mobile','level','ip','format_lottery_time','prize_name')
	search_fields = ('username','mobile', 'prize_name')
	list_filter = (
        ('lottery_time', DateFieldListFilter),
    )
	def format_lottery_time(self,obj):
		return obj.lottery_time.strftime('%Y-%m-%d, %H:%M:%S')
		

class PrizeConfigurationAdmin(admin.ModelAdmin):
	list_display = ('prize','lottery_date','count','use_count')
	def lottery_date(self,obj):
		return obj.date.strftime('%Y-%m-%d')


admin.site.register(Question,QuestionAdmin)
admin.site.register(Prize,PrizeAdmin)
admin.site.register(LotteryRecord,LotteryRecordAdmin)
admin.site.register(PrizeConfiguration,PrizeConfigurationAdmin)
admin.site.register(Coupon,CouponAdmin)
