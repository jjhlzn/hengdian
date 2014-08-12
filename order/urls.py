from django.conf.urls import patterns, url

from order import views

urlpatterns = patterns('',
    url(r'^$', views.index, name='index'),
    url(r'^order_statistic$',views.order_statistic, name='order_statistic'),
)
