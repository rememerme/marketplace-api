'''
    This file holds all of the forms for the cleaning and validation of
    the parameters being used for friend requests.
    
    Created on Dec 20, 2013

    @author: Andrew Oberlin, Jake Gregg
'''
from django import forms
from rememerme.games.models import Game, GameMember
from rememerme.games.rest.exceptions import InvalidWinningScore, GameNotFound,\
    BadRequestException
from rememerme.games.serializers import GameSerializer, GameMemberSerializer
from uuid import UUID
import uuid
from pycassa.cassandra.ttypes import NotFoundException as CassaNotFoundException
import datetime
import json
from rememerme.games.permissions import GamePermissions
from rememerme.users.client import UserClient, UserClientError

class GamesListGetForm(forms.Form):

    def submit(self, request):
        try:
            game_memberships = GameMember.filterByUser(request.user.pk)
            games = [Game.getByID(mem.game_id) for mem in game_memberships]
        except CassaNotFoundException:
            raise GameNotFound()
        return GameSerializer(games, many=True).data

'''
    Creates a new game instance.
'''
class GamesPostForm(forms.Form):
    game_members = forms.CharField(required=True)
    winning_score = forms.IntegerField(required=True)

    def clean(self):
        '''
            Overriding the clean method to add the default offset and limiting information.
        '''
        now = datetime.datetime.now()
        self.cleaned_data['date_created'] = now
        self.cleaned_data['last_modified'] = now
        
        if self.cleaned_data['winning_score'] <= 0:
            raise InvalidWinningScore()
        
        try:
            self.cleaned_data['game_members'] = json.loads(self.cleaned_data['game_members'])
            if not isinstance(self.cleaned_data['game_members'], list):
                raise BadRequestException()
        except ValueError:
            raise BadRequestException()
        
        return self.cleaned_data
    
    
    def submit(self, request):
        '''
            Submits this form to create the given game.
        '''
        game_members = self.cleaned_data['game_members']
        del self.cleaned_data['game_members']
        self.cleaned_data['leader_id'] = UUID(request.user.pk)
        game = Game.fromMap(self.cleaned_data)
        game.save()
        
        members_added = {}
        
        for mem in game_members:
            try:
                mem = str(UUID(mem))
                UserClient(request.auth).get(mem)
                # user exists so let's add him/her
                now = datetime.datetime.now()
                member = GameMember(game_member_id=str(uuid.uuid1()), game_id=UUID(game.game_id), user_id=UUID(mem), status=1, date_created=now, last_modified=now)
                member.save()
                members_added[member.game_member_id] = now
            except ValueError, UserClientError:
                continue
       
        member = GameMember(game_member_id=str(uuid.uuid1()), score=0, game_id=UUID(game.game_id), user_id=UUID(request.user.pk), status=2, date_created=now, last_modified=now)
        member.save()
        members_added[member.game_member_id] = now 

        serialized = GameSerializer(game).data
        serialized['game_members'] = members_added
        return serialized

class GamesSingleGetForm(forms.Form):
    game_id = forms.CharField()
    
    def clean(self):
        try:
            self.cleaned_data['game_id'] = str(UUID(self.cleaned_data['game_id']))
        except ValueError:
            raise GameNotFound()
        return self.cleaned_data

    def submit(self, request):
        try:
            game = Game.getByID(self.cleaned_data['game_id'])
            if not GamePermissions.has_object_permission(request, game):
                raise BadRequestException()
        except CassaNotFoundException:
            raise GameNotFound()
        return GameSerializer(game).data

class GameRequestsForm(forms.Form):
    def submit(self, request):
        requests = [gm for gm in GameMember.filterByUser(request.user.pk) if gm.status == 1]
        return GameMemberSerializer(requests, many=True).data
        
        
        
        

