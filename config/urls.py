from django.conf.urls import patterns, include, url

urlpatterns = patterns('',
    url(r'^rest/v1/phrase_decks/(?P<game_id>[-\w]+)/cards', include('rememerme.markeplace.rest.phrase_cards.urls')),
    url(r'^rest/v1/nomination_decks/(?P<game_id>[-\w]+)/cards', include('rememerme.games.rest.nomination_cards.urls')),
    url(r'^rest/v1/phrase_decks', include('rememerme.markeplace.rest.phrase_decks.urls')),
    url(r'^rest/v1/nomination_decks', include('rememerme.marketplace.rest.nomination_decks.urls')),
    url(r'^rest/v1/account/purchases', include('rememerme.markeplace.rest.purchases.urls')),
    url(r'^rest/v1/account/wallet', include('rememerme.marketplace.rest.wallet.urls'))
)
