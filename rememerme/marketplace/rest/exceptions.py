from rest_framework.exceptions import APIException

class BadRequestException(APIException):
    '''
        Bad Request Exception.
    '''
    status_code = 400
    detail = "A Bad Request was made for the API. Revise input parameters."
    
class InvalidWinningScore(APIException):
    '''
        The winning score was not greater than 0.
    '''
    status_code = 400
    detail = "You can't setup a game if the score doesn't make sense."

class IllegalStatusCode(APIException):
    '''
        The code for the game member status is out of range.
    '''
    status_code = 40
    detail = "The code for the game member status is out of range."

class GameNotFound(APIException):
    '''
        The game requested was not found.
    '''
    status_code = 404
    detail = "Don't ask about that game because we have no idea what you are talking about."
    
class RoundNotFound(APIException):
    '''
        The round requested was not found.
    '''
    status_code = 404
    detail = "That round doesn't seem to be a thing."
    
class NotTheSelector(APIException):
    '''
        The user tried to select without being the selector.
    '''
    status_code = 400
    detail = "Wait your turn to select."

class GameMemberNotFound(APIException):
    '''
        The game member was not found
    '''
    status_code = 404
    detail = "You are not apparently part of this game or something."

class GameMemberAlreadyExists(APIException):
    '''
        Game Memberalready exists.
    '''
    status_code = 404
    detail = "You've already invited him to the game! Be more needy!"

class GameAlreadyStarted(APIException):
    '''
        The game has already been started and will not be restarted.
    '''
    status_code = 404
    detail = "The game has already begun."  
    
class NoCurrentRound(APIException):
    '''
        The game does not have a current round.
    '''
    status_code = 404
    detail = "You have to start the game for that!"
    
class AlreadyNominated(APIException):
    '''
        The player already made his nomination.
    '''
    status_code = 400
    detail = "You already made your move. No takesies backsies mister!"
    
class InvalidNominationCard(APIException):
    '''
        The player submitted a card that is not real.
    '''
    status_code = 400
    detail = "You provided a card that does not exist."
    
class PhraseCardNotFound(APIException):
    '''
        The player submitted a card that is not real.
    '''
    status_code = 404
    detail = "That phrase card that does not exist."
