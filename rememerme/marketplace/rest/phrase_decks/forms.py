'''
    This file holds all of the forms for the cleaning and validation of
    the parameters being used for friend requests.
    
    Created on Dec 20, 2013

    @author: Andrew Oberlin, Jake Gregg
'''
from django import forms
from rememerme.games.models import GameMember
from rememerme.games.rest.exceptions import IllegalStatusCode, GameNotFound,\
    BadRequestException, GameMemberNotFound, GameMemberAlreadyExists
from rest_framework.exceptions import PermissionDenied
from rememerme.games.serializers import GameMemberSerializer
from uuid import UUID
from pycassa.cassandra.ttypes import NotFoundException as CassaNotFoundException
import datetime

class GameMembersPutForm(forms.Form):
    game_id = forms.CharField(required=True)
    status = forms.IntegerField(required=True)

    def clean(self):
        try:
            self.cleaned_data['game_id'] = str(UUID(self.cleaned_data['game_id']))
        except ValueError:
            raise GameMemberNotFound()
        
        if self.cleaned_data['status'] < 0 or self.cleaned_data['status'] > 2:
            raise IllegalStatusCode()
        
        return self.cleaned_data

    def submit(self, request):
        try:
            # get the game member by the group and user combination
            members = GameMember.filterByGame(self.cleaned_data['game_id'])
            member = None
            for m in members:
                if str(m.user_id) == request.user.pk:
                    member = m
                    break
            if not member:
                raise GameMemberNotFound()
            
            member.status = self.cleaned_data['status']
            member.save()
        except CassaNotFoundException:
            raise GameMemberNotFound()
        return GameMemberSerializer(member).data

'''
    Creates a new game instance.
'''
class GameMembersPostForm(forms.Form):
    game_id = forms.CharField(required=True)
    user_id = forms.CharField(required=True)

    def clean(self):
        '''
            Overriding the clean method to add the default offset and limiting information.
        '''
        try:
            self.cleaned_data['game_id'] = str(UUID(self.cleaned_data['game_id']))
            self.cleaned_data['user_id'] = str(UUID(self.cleaned_data['user_id']))
        except ValueError:
            raise BadRequestException()
        
        now = datetime.datetime.now()
        self.cleaned_data['date_created'] = now
        self.cleaned_data['last_modified'] = now
        self.cleaned_data['status'] = 1
        
        return self.cleaned_data
    
    
    def submit(self, request):
        '''
            Submits this form to create the given game.
        '''
        members = GameMember.filterByGame(self.cleaned_data['game_id'])
        them = None
        me = None
        for m in members:
            if str(m.user_id) == request.user.pk:
                me = m
            if str(m.user_id) == self.cleaned_data['user_id']:
                them = m
                
            if them and me:
                break
        if them:
            raise GameMemberAlreadyExists()
        
        if not me:
            raise PermissionDenied()
        
        member = GameMember.fromMap(self.cleaned_data)
        member.save()
        
        return GameMemberSerializer(member).data

class GameMembersGetForm(forms.Form):
    game_id = forms.CharField()
    
    def clean(self):
        try:
            self.cleaned_data['game_id'] = str(UUID(self.cleaned_data['game_id']))
        except ValueError:
            raise GameNotFound()
        return self.cleaned_data

    def submit(self, request):
        try:
            members = GameMember.filterByGame(self.cleaned_data['game_id'])
            member_ids = set([str(m.user_id) for m in members])
            if request.user.pk not in member_ids:
                raise PermissionDenied()
        except CassaNotFoundException:
            raise GameNotFound()
        
        return GameMemberSerializer(members, many=True).data


