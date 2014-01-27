'''
    This file holds all of the forms for the cleaning and validation of
    the parameters being used for friend requests received.
    
    Created on Dec 20, 2013

    @author: Andrew Oberlin, Jake Gregg
'''
from django import forms
from rememerme.games.models import Game, Round, GameMember, Nomination
from rememerme.cards.models import PhraseCard, NominationCard
from rememerme.games.rest.exceptions import NoCurrentRound, RoundNotFound, \
    GameNotFound, GameAlreadyStarted, AlreadyNominated, InvalidNominationCard, NotTheSelector
from rememerme.games.serializers import RoundSerializer, NominationSerializer
from uuid import UUID
from pycassa.cassandra.ttypes import NotFoundException as CassaNotFoundException
import datetime
import random
from rememerme.games.permissions import GamePermissions
from rest_framework.exceptions import PermissionDenied

'''
    Gets all friend requests recieved and returns them to the user.

    @return: A list of requests matching the query with the given offset/limit
'''        
class StartGameForm(forms.Form):
    game_id = forms.CharField(required=True)
    deck_id = forms.CharField(required=True)
    
    def clean(self):
        try:
            self.cleaned_data['game_id'] = str(UUID(self.cleaned_data['game_id']))
            self.cleaned_data['deck_id'] = str(UUID(self.cleaned_data['deck_id']))
        except ValueError:
            raise GameNotFound()
        return self.cleaned_data
    
    
    '''
        Submits the form and returns the friend requests received for the user.
    '''
    def submit(self, request):
        try:
            game = Game.getByID(self.cleaned_data['game_id'])
            if game.current_round_id:
                raise GameAlreadyStarted()
        except CassaNotFoundException:
            raise GameNotFound()
        
        if not GamePermissions.has_object_permission(request, game):
            raise PermissionDenied()
        
        # select randomly from the game members
        game_members = GameMember.filterByGame(game.game_id)
        selector = random.choice(game_members)
        
        now = datetime.datetime.now()
        
        round = Round(selector_id=selector.user_id, phrase_card_id=PhraseCard.getRandom(self.cleaned_data['deck_id']).phrase_card_id,
            game_id=game.game_id, date_created=now, last_modified=now)
        
        round.save()
        
        game.deck = self.cleaned_data['deck_id']
        game.current_round_id = round.round_id
        game.save()

        return RoundSerializer(round).data
    
'''
    Accepts a friend request for a user.

    @return: Validation of accepting the request.
'''
class RoundForm(forms.Form):
    game_id = forms.CharField(required=True)
    
    def clean(self):
        cleaned_data = super(RoundForm, self).clean()
        try:
            cleaned_data['game_id'] = str(UUID(cleaned_data['game_id']))
        except ValueError:
            raise GameNotFound()
        return cleaned_data
    
    def submit(self, request):
        game_id = self.cleaned_data['game_id']
        
        try:
            game = Game.getByID(game_id)
        except CassaNotFoundException:
            raise GameNotFound()
        
        if not GamePermissions.has_object_permission(request, game):
            raise PermissionDenied()
        
        try:
            if not game.current_round_id:
                raise NoCurrentRound()
            round = Round.getByID(game.current_round_id)
        except CassaNotFoundException:
            raise NoCurrentRound()
        
        return RoundSerializer(round).data
        

'''
    Denies a friend request for the user.

    @return: confirmation that the request was denied.
'''
class NominationsGetForm(forms.Form):
    game_id = forms.CharField(required=True)
    
    def clean(self):
        try:
            self.cleaned_data['game_id'] = str(UUID(self.cleaned_data['game_id']))
            return self.cleaned_data
        except ValueError:
            raise GameNotFound()
    
    '''
        Submits the form to deny the friend request.
    '''
    def submit(self, request):
        game = Game.getByID(self.cleaned_data['game_id'])
        if not game.current_round_id:
            raise NoCurrentRound()
        
        if not GamePermissions.has_object_permission(request, game):
            raise PermissionDenied()
        
        nominations = Nomination.filterByRound(game.current_round_id)
        return NominationSerializer(nominations, many=True).data

'''
    Denies a friend request for the user.

    @return: confirmation that the request was denied.
'''
class NominationsPostForm(forms.Form):
    game_id = forms.CharField(required=True)
    nomination_card_id = forms.CharField(required=True)
    
    def clean(self):
        try:
            self.cleaned_data['game_id'] = str(UUID(self.cleaned_data['game_id']))
            self.cleaned_data['nomination_card_id'] = str(UUID(self.cleaned_data['nomination_card_id']))
            return self.cleaned_data
        except ValueError:
            raise GameNotFound()
    
    '''
        Submits the form to deny the friend request.
    '''
    def submit(self, request):
        game = Game.getByID(self.cleaned_data['game_id'])
        if not game.current_round_id:
            raise NoCurrentRound()
        
        if not GamePermissions.has_object_permission(request, game):
            raise PermissionDenied()
        
        nominations = Nomination.filterByRound(game.current_round_id)
        users = set([str(n.nominator_id) for n in nominations])
        if request.user.pk in users:
            raise AlreadyNominated()
        
        now = datetime.datetime.now()
        try:
            NominationCard.getByID(self.cleaned_data['nomination_card_id'])
        except CassaNotFoundException:
            raise InvalidNominationCard()
        
        nomination = Nomination(round_id=game.current_round_id, nominator_id=request.user.pk,
                nomination_card_id=self.cleaned_data['nomination_card_id'], date_created=now, last_modified=now)
        nomination.save()
        
        return NominationSerializer(nomination).data
        
'''
    Denies a friend request for the user.

    @return: confirmation that the request was denied.
'''
class SelectionForm(forms.Form):
    game_id = forms.CharField(required=True)
    selection_id = forms.CharField(required=True)
    
    def clean(self):
        try:
            self.cleaned_data['game_id'] = str(UUID(self.cleaned_data['game_id']))
            self.cleaned_data['selection_id'] = str(UUID(self.cleaned_data['selection_id']))
            return self.cleaned_data
        except ValueError:
            raise GameNotFound()
    
    '''
        Submits the form to deny the friend request.
    '''
    def submit(self, request):
        try:
            game = Game.getByID(self.cleaned_data['game_id'])
        except CassaNotFoundException:
            raise GameNotFound()
        
        if not GamePermissions.has_object_permission(request, game):
            raise PermissionDenied()
        
        if not game.current_round_id:
            raise NoCurrentRound()
        try:
            round = Round.getByID(game.current_round_id)
        except CassaNotFoundException:
            raise RoundNotFound()
        
        if request.user.pk != str(round.selector_id):
            raise NotTheSelector()
        
        try:
            nomination = Nomination.getByID(self.cleaned_data['selection_id'])
        except CassaNotFoundException:
            raise InvalidNominationCard()
        
        round.selection_id = self.cleaned_data['selection_id']
        round.save()
        
        game_members = GameMember.filterByGame(game.game_id)
        # finds the game state that should be updated
        member = None
        for m in game_members:
            if str(m.user_id) == str(nomination.nominator_id):
                member = m
                break
        
        member.score += 10
        member.save()
        
        # creates a new round, saves it and the game
        now = datetime.datetime.now()
        selector = random.choice(game_members)
        
        new_round = Round(selector_id=selector.user_id, phrase_card_id=PhraseCard.getRandom(game.deck).phrase_card_id,
            game_id=game.game_id, date_created=now, last_modified=now)
        
        new_round.save()
        
        game.current_round_id = new_round.round_id
        game.save()
        
        return RoundSerializer(new_round).data
        
        
        
        
        
        
        
        
        
        
