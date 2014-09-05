from django.conf.urls import patterns, url

from order.views import views_report
from order.views import views_search
from order.views import views_ticketsystem_report

urlpatterns = patterns('',
    url(r'^$', views_report.order_statistic, name='order_statistic'),
    url(r'^order_statistic$',views_report.order_statistic, name='order_statistic'),
    url(r'^ticketorder_stat',views_report.ticketorder_stat, name='ticketorder_stat'),
    url(r'^json/order_statistic$',views_report.order_statistic_json, name='order_statistic_json'),
    url(r'^ts_order_stat', views_ticketsystem_report.ts_order_stat, name='ts_order_stat'),
    url(r'^json/ts_order_stat$', views_ticketsystem_report.order_statistic_json, name='ts_order_stat_json'),
    url(r'^order_search$', views_search.order_search, name='order_search'),
)
