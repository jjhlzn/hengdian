from django.contrib import admin
from lottery.models import Question, Prize, LotteryRecord,PrizeConfiguration,Coupon


class PrizeAdmin(admin.ModelAdmin):
	list_display = ('name','quantity')

class CouponAdmin(admin.ModelAdmin):
	list_display = ('name','code','status')
	
class LotteryRecordAdmin(admin.ModelAdmin):
	list_display = ('username','mobile','ip','lottery_time','prize_name')



admin.site.register(Question)
admin.site.register(Prize,PrizeAdmin)
admin.site.register(LotteryRecord,LotteryRecordAdmin)
admin.site.register(PrizeConfiguration)
admin.site.register(Coupon,CouponAdmin)
