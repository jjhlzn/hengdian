from django.conf.urls import patterns, url

from lottery import views

urlpatterns = patterns('',
	url(r'^choujiang_step/$', views.choujiang_step, name='choujiang_step'),
	url(r'^choujiang_handle/$', views.choujiang_handle, name='choujiang_handle'),
	#url(r'^choujiang_result_yes/$', views.choujiang_result_yes, name='choujiang_result_yes'),
	#url(r'^choujiang_result_no/$', views.choujiang_result_no, name='choujiang_result_no'),
    url(r'^$', views.index, name='index')
	
)