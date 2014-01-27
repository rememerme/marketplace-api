from django.conf.urls import patterns, url

from rememerme.games.rest.rounds import views

urlpatterns = patterns('',
    url(r'^/?$', views.StartGameView.as_view()),
    url(r'^/current/?$', views.RoundView.as_view()),
    url(r'^/current/nominations/?$', views.NominationsView.as_view()),
    url(r'^/current/selection/?$', views.SelectionView.as_view())
)
