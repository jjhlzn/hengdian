from django.conf.urls import patterns, url

from lottery import views

urlpatterns = patterns('',
	url(r'^choujiang_step/$', views.choujiang_step, name='choujiang_step'),
	url(r'^choujiang_handle/$', views.choujiang_handle, name='choujiang_handle'),
	url(r'^choujiang_result/$', views.choujiang_result, name='choujiang_result'),
	url(r'^choujiang_search/$', views.choujiang_search, name='choujiang_search'),
    url(r'^$', views.index, name='index')
	
)