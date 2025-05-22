
from celery import shared_task

from django.utils               import timezone

from user_mgr.models            import AutologinToken

from common.date                import get_yesterday

from emailing.tools             import sendmail_template, MessageType

from paybox                     import LEVEL_PUBLIC_NAMES
from paybox.controller          import get_user_best_tariff_str
from paybox.models              import Subscription


@shared_task
def delete_expired_tokens():
    """
    Remove old autologin tokens
    """
    AutologinToken.objects.filter(valid_until__lte=timezone.now()).delete()

@shared_task
def expired_subscription_email(simulate=False):
    """
    Send an email to all the users arriving at the end of their subscription (trial or paid)
    """
    expired = Subscription.objects.filter(end_date=get_yesterday(), cancelled=False).order_by('id')

    for subscription in expired:

        if subscription.total_amount == 0:
            template = 'cookandbe/templates/expired_trial.html'
            tag = 'expired_trial'
            title = "Votre période d'essai est terminée"
        else:
            template = 'cookandbe/templates/expired_subscription.html'
            tag = 'expired_subscription'
            title = "Votre abonnement est expiré"

        template_args = {}

        if subscription.user.diet.key != 'balanced':
            template_args['diet'] = subscription.user.diet.email_title
        template_args['subscription'] = LEVEL_PUBLIC_NAMES[subscription.level]
        template_args['best_tariff'] = get_user_best_tariff_str(subscription.user, subscription.level)

        sendmail_template(MessageType.NOTIFICATION, template, template_args, title,
                          users=[subscription.user], send_async=not simulate, tags=[tag])
