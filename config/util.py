'''
    Gets the offset and limit parameters from the request with the
    proper offset and limit settings.

    Created on Dec 20, 2013

    @author: Andrew Oberlin
'''

from django.conf import settings

'''
    Gets the correct value for the offset and limit based on the application
    settings.
    
    @param request: The request being made to the server
'''
def getLimit(request):
    limit = settings.REST_FRAMEWORK['PAGINATE_BY']
    
    # gets the limit of the request and defaults to the maximum if the limit passed is too big
    # also if no limit is sent then the limit in the settings is used
    if 'limit' in request and request['limit']:
        maxLimit = settings.REST_FRAMEWORK['MAX_PAGINATE_BY']
        limit = maxLimit if request['limit'] > maxLimit else request['limit']
    
    return limit