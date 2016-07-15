from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^new_tournament/', views.new_tor, name='new_tor'),
    url(r'^api/tournament/(?P<_tour_id>\d+)/', views.tournament_api, name='tournament_api'),
    url(r'^tournament/(?P<_tour_id>\d+)/', views.tournament, name='tournament'),
	url(r'^who_online/', views.who_online, name='who_online'),
]