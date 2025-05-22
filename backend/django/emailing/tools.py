
from django.template.loader         import get_template
from django.shortcuts               import render
from django.utils                   import timezone
from django.conf                    import settings

from emailing                       import SendmailError, MessageType
from emailing.tasks                 import send_email

import datetime
import premailer
import logging

# Default expire time is 1H : if it fails to be sent after 1H, it is abandoned
DEFAULT_MAIL_EXPIRATION_DELAY = 60 * 60

def filter_users(users, message_type):
    """
    Make sure not to send emails to users who unsubscribe
    """
    if message_type == MessageType.REALTIME:
        return users  # No filter on emails like password reminder
    users = filter(lambda x: x.enabled, users) # Don't send emails to users that unsubscribe
    if message_type == MessageType.NEWSLETTER:
        return filter(lambda x: x.mail_newsletter, users)
    if message_type == MessageType.DAILY:
        return filter(lambda x: x.mail_daily, users)
    if message_type == MessageType.NOTIFICATION:
        return filter(lambda x: x.mail_notifications, users)
    assert message_type == MessageType.MAIN_INFO, "invalid message type : %s" % message_type
    return users

def sendmail(message_type, subject, message, email=None, users=None, emitter=None,
             tags=None, send_async=False, eta=None, expires=None, with_bcc=True):
    """
    Send a mail to a list of users or emails
    @param send_async: if true, will be sent asynchronously using Celery
    @param eta: (send_async=True required) will be sent at a given datetime
    """
    # Initialisation
    if emitter is None: emitter = ""
    if users is not None:
        users = filter_users(users, message_type)
        receivers = [{'email': user.email, 'name': user.first_name, 'type': 'to'} for user in users]
        assert email is None, "cannot set users and email. Use one or the other"
    if email is not None:
        receivers = [{'email': email, 'name': email, 'type': 'to'}]
    if len(receivers) == 0:
        return
    if tags is None: tags = []

    # Making the HTML mail-compatible
    premail = premailer.Premailer(message, cssutils_logging_level=logging.ERROR)

    # MANY other options available here : https://mandrillapp.com/api/docs/messages.python.html
    message = {
        'auto_text': True, # Automatic conversion of HTML to text for text-only mailboxes
        'from_email': 'noreply@%s' % settings.FROM_EMAIL_HOST,
        'from_name': settings.APP_BRAND_NAME.replace('&', ' and '),
        'headers': {'Reply-To': 'noreply@%s' % settings.FROM_EMAIL_HOST},
        'html': premail.transform(),
        'important': False,
        'inline_css': True,  # Distinct CSS doesn't work in most email boxes
        'preserve_recipients': False,
        'subject': subject,
        'tags': tags,
        'to': receivers,
        'track_clicks': True,
        'track_opens': True
    }
    if with_bcc and settings.ENABLE_AUTO_BCC:
        message['bcc_address'] = 'cc@%s' % settings.FROM_EMAIL_HOST
    if send_async:
        if type(eta) is int:
            eta = timezone.now() + datetime.timedelta(seconds=eta)
        kargs = {'args': [message], 'eta': eta}
        if expires is None:
            expires = DEFAULT_MAIL_EXPIRATION_DELAY
        if eta is not None and type(expires) is not datetime.datetime:
            # If there is an ETA, and expires is in seconds, calculate the expiration time
            expires = eta + datetime.timedelta(seconds = expires)
        kargs['expires'] = expires
        # Sending it asynchronously
        send_email.apply_async(**kargs)
    else:
        # Sending it right now
        send_email(message)


def sendmail_template(message_type, template_path, template_vars, subject, email = None, users = None,
                      emitter = None, tags = None, send_async=False, eta=None, expires=None,
                      no_personal_infos=False, with_bcc=True):
    """
    if "users" is given, and contains only one user, personal information (objective, imc, nb_recipes) will be automatically retrieved and added
    """
    assert 'title' not in template_vars, "title value is automatically added in template_vars, from subject argument"
    template_vars['title'] = subject
    t = get_template(template_path)
    if users is None or len(users) > 1:
        assert no_personal_infos, "Add no_personal_infos=True if you accept not to have details on user. Otherwise, call sendmail_template with one user only"
    if not no_personal_infos:
        user = users[0]
        template_vars['username'] = user.first_name
        template_vars['objective'] = user.activated_diet.title
        template_vars['imc_value'] = round(user.main_profile.imc, 1)
        template_vars['imc_name'] = user.main_profile.imc_caption
        template_vars['nb_recipes'] = user.written_recipes.filter(internal=False).count()
    message = t.render(template_vars)

    return sendmail(message_type, subject, message, email=email, users=users, emitter=emitter,
                    tags=tags, send_async=send_async, eta=eta, expires=expires, with_bcc=with_bcc)
