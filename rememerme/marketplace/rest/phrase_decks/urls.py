from django.conf.urls import patterns, url

from rememerme.games.rest.members import views

urlpatterns = patterns('',
    url(r'^/?', views.GameMembersView.as_view())
)
