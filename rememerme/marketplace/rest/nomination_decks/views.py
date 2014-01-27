from rest_framework.views import APIView
from rest_framework.response import Response
from rememerme.games.rest.rounds.forms import StartGameForm, RoundForm, NominationsGetForm, NominationsPostForm, SelectionForm
from rememerme.games.rest.exceptions import BadRequestException
from rest_framework.permissions import IsAuthenticated

class StartGameView(APIView):
    permission_classes = (IsAuthenticated,)
    
    '''
       Used for searching by properties or listing all friend requests received available.
    '''
    
    def post(self, request, game_id):
        '''
            Used to get all friends requests receieved of a user
        '''
        data = { key : request.DATA[key] for key in request.DATA }
        data['game_id'] = game_id
        
        # get the offset and limit query parameters
        form = StartGameForm(data)
        
        if form.is_valid():
            return Response(form.submit(request))
        else:
            raise BadRequestException()
        
class RoundView(APIView):
    permission_classes = (IsAuthenticated,)
    
    '''
       Accepting, denying, and viewing requests received.
    '''     
    
    def get(self, request, game_id):
        '''
            Accept friend request.
        '''
        data = { key : request.QUERY_PARAMS[key] for key in request.QUERY_PARAMS }
        data['game_id'] = game_id
        form = RoundForm(data)

        if form.is_valid():
            return Response(form.submit(request))
        else:
            raise BadRequestException()
        
class NominationsView(APIView):
    permission_classes = (IsAuthenticated,)
    
    '''
       Accepting, denying, and viewing requests received.
    '''     
    
    def get(self, request, game_id):
        '''
            Accept friend request.
        '''
        data = { key : request.QUERY_PARAMS[key] for key in request.QUERY_PARAMS }
        data['game_id'] = game_id
        form = NominationsGetForm(data)

        if form.is_valid():
            return Response(form.submit(request))
        else:
            raise BadRequestException()
        
    def post(self, request, game_id):
        '''
            Used to get all friends requests receieved of a user
        '''
        data = { key : request.DATA[key] for key in request.DATA }
        data['game_id'] = game_id
        
        # get the offset and limit query parameters
        form = NominationsPostForm(data)
        
        if form.is_valid():
            return Response(form.submit(request))
        else:
            raise BadRequestException()
        
class SelectionView(APIView):
    permission_classes = (IsAuthenticated,)
    
    '''
       Accepting, denying, and viewing requests received.
    '''     
        
    def post(self, request, game_id):
        '''
            Used to get all friends requests receieved of a user
        '''
        data = { key : request.DATA[key] for key in request.DATA }
        data['game_id'] = game_id
        
        # get the offset and limit query parameters
        form = SelectionForm(data)
        
        if form.is_valid():
            return Response(form.submit(request))
        else:
            raise BadRequestException()

