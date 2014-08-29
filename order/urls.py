from django.conf.urls import patterns, url

from order.views import views_report
from order.views import views_search

urlpatterns = patterns('',
    url(r'^$', views_report.order_statistic, name='order_statistic'),
    url(r'^order_statistic$',views_report.order_statistic, name='order_statistic'),
    url(r'^ticketorder_stat',views_report.ticketorder_stat, name='ticketorder_stat'),
    url(r'^order_search$', views_search.order_search, name='order_search'),
)
