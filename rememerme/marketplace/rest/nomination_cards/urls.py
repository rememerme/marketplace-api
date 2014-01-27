from django.conf.urls import patterns, url

from rememerme.games.rest.games import views

urlpatterns = patterns('',
    url(r'^/requests/?', views.GameRequestView.as_view()),
    url(r'^/(?P<game_id>[-\w]+)/?', views.GamesSingleView.as_view()),
    url(r'^/?$', views.GamesListView.as_view())
)
