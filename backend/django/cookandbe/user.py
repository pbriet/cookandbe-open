
from emailing.tools             import sendmail_template, MessageType

import datetime

# 10 days
POLL_MAIL_DELAY = 60 * 60 * 24 * 10

def first_visit_poll_mail(user, profile, simulate = False):
    """
    10 days after inscription, send a link to a google form
    """
    template_vars = {
        'nickname': profile.nickname,
        'usermail': user.email,
        'userid': user.id,
    }
    sendmail_template(
        MessageType.MAIN_INFO ,
        'cookandbe/templates/first_visit_poll.html',
        template_vars,
        "Donnez-nous votre avis sur Cook&Be",
        users   = [user, ],
        send_async   = not simulate,
        eta     = POLL_MAIL_DELAY,
        tags    = ['poll', 'first_visit'],
    )

def welcome_mail(user, profile):
    """
    Send a welcome email
    """
    template_vars = { "nickname" : profile.nickname }
    sendmail_template(
        MessageType.REALTIME,
        'cookandbe/templates/welcome.html',
        template_vars,
        "Bienvenue sur Cook and Be !",
        email               = user.email,
        no_personal_infos   = True,
        send_async          = True,
        tags                = ['welcome'],
    )
