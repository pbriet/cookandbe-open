import traceback

from optalim.log import logger
"""
Middleware that logs any exception as a critical info
(Handling logs is defined in settings.py LOGGING attribute)
"""

class ExceptionMiddleware(object):

    def __init__(self, get_response=None):
        self.get_response = get_response

    def process_exception(self, request, exception):
        #logging.exception('Exception catched')
        exception_text = "Error with Query %s\n" % request.path
        exception_text += traceback.format_exc()
        logger.error(exception_text, extra={'ct_request': request})
        return

    def __call__(self, request):
        response = self.get_response(request)
        if response.status_code == 404:
            print("HTTP 404 : %s" % request.path)

        if response.status_code == 400:
            logger.error("HTTP 400 : %s -- %s" % (request.path, response.content), extra={'ct_request': request})

        return response
