from django.conf.urls import patterns, url

from lottery import views

urlpatterns = patterns('',
    url(r'^$', views.index, name='index')
)