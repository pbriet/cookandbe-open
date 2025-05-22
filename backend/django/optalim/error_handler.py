import traceback

from django.conf        import settings
from django.core        import mail
from django.http        import QueryDict
from django.utils.log   import AdminEmailHandler
from django.views.debug import ExceptionReporter, get_exception_reporter_filter


class BodySaveMiddleware(object):
    """
    Read the body, and store it if content length is less than 1000 chars,
    for debugging purposes
    """
    def __init__(self, get_response=None):
            self.get_response = get_response

    def __call__(self, request):
        """
        Django 1.10 version
        """
        try:
            content_length = int(request.META.get('CONTENT_LENGTH', 10000))
            if content_length < 1000:
                try:
                    request._body_log = request.body.decode('utf-8')
                except:
                    request._body_log = "(failed to get body)"
        except:
            pass

        return self.get_response(request)


class CustomAdminEmailHandler(AdminEmailHandler):
    """
    Customized email for admins in case of crash
    """

    def emit(self, record):
        user_id = "unknown"
        user_email = "unknown"
        error_message = record.getMessage()
        request = None
        try:
            request = record.ct_request
            try:
                if request.user is None or request.user.id is None:
                    user_id = "no"
                else:
                    user_id = request.user.id
                    user_email = request.user.email
            except:
                pass
            subject = '%s [user=%s] %s' % (
                record.levelname, user_id,
                request.path
            )
            filter = get_exception_reporter_filter(request)
        except Exception as e:
            subject = '%s: %s' % (
                record.levelname, error_message
            )

        subject = self.format_subject(subject)

        if record.exc_info:
            exc_info = record.exc_info
            stack_trace = '\n'.join(traceback.format_exception(*record.exc_info))
        else:
            exc_info = (None, record.getMessage(), None)
            stack_trace = 'No stack trace available'

        body = ""
        if request is not None:
            try:
                body = request._body_log
            except:
                body = "(error when retrieving body)"

        message = "ERROR : %s\n\n\n" % error_message
        message += "USER ID : %s\n" % user_id
        message += "USER EMAIL : %s\n\n" % user_email
        message += "BODY : %s\n\n" % body
        reporter = ExceptionReporter(request, is_email=True, *exc_info)

        mail.mail_admins(subject, message, fail_silently=True,
                         connection=self.connection())

