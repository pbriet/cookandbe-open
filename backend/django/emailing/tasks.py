"""
Asynchronous tasks handled by celery
"""

from celery                 import shared_task

from common.string          import unaccent

from emailing               import SendmailError


from optalim.settings       import TESTING, DEBUG_LOGS_DIR, EMAIL_MODE, SENDGRID_API_KEY, ENABLE_EMAILS

from django.utils import timezone

import os
import re
import codecs
import sendgrid
import sendgrid.helpers.mail as sg_helpers

from optalim.log import logger

@shared_task
def send_email(message):
    if TESTING or EMAIL_MODE == 'log':
        return log_email(message)
    if not ENABLE_EMAILS:
        print("Emailing is disabled on this server")
        print("Skipping mail")
        return "skipped"
    if EMAIL_MODE == 'send_to_staging':
        message['subject'] = '[STAGING] ' + message['subject']
        to_emails = ";".join(to['email'] for to in message['to'])
        message['html'] = message['html'].replace('<!-- STAGING_REPLACE -->', '<b>SENT TO : %s</b><br/><br/><br/>' % to_emails)
        message['to'] = [{'email': 'preprod@cookandbe.com', 'name': 'Staging', 'type': 'to'}]
        message['track_clicks'] = message['track_opens'] = False
        if 'bcc_address' in message:
            del message['bcc_address']
        return really_send_sendgrid_email(message)
    if EMAIL_MODE == 'send':
        return really_send_sendgrid_email(message)


def log_email(message):
    logger.info('DEBUG : [not] sending email %s (to %i receivers)' % (message['subject'], len(message['to'])))
    if not TESTING:
        # Saving the message into a HTML file instead of sending it.
        message_normalized = unaccent(re.compile('\W+').sub('', message['subject'].lower()).strip())
        if len(message_normalized) > 10:
            message_normalized = message_normalized[:10]
        log_filename = "%s_%s.html" % (timezone.now().strftime("%Y%m%d%H%M%S"), message_normalized)
        f = codecs.open(os.path.join(DEBUG_LOGS_DIR, log_filename), "w", encoding='utf8')
        f.write(message['html'])
        f.close()
        logger.info('DEBUG : message dumped into %s' % log_filename)
    return "cannot_send - debug"

def really_send_sendgrid_email(message):
    """
    Send email through Sendgrid
    """
    sg = sendgrid.SendGridAPIClient(api_key=SENDGRID_API_KEY)

    perso = sg_helpers.Personalization()

    receivers = message['to']
    for r in receivers:
        if r.get('type', 'to') == 'cc':
            perso.add_cc(sg_helpers.Email(r['email']))
        if r.get('type', 'to') == 'to':
            perso.add_to(sg_helpers.Email(r['email']))
        if r.get('type', 'to') == 'bcc':
            perso.add_bcc(sg_helpers.Email(r['email']))
    if message.get('bcc_address', ''):
        perso.add_bcc(sg_helpers.Email(message['bcc_address']))

    mail = sg_helpers.Mail()
    mail.add_personalization(perso)
    mail.from_email = sg_helpers.Email(message['from_email'], message['from_name'])
    mail.subject = message['subject']
    mail.add_content(sg_helpers.Content("text/html", message['html']))

    response = sg.client.mail.send.post(request_body=mail.get())

    if str(response.status_code)[:2] != "20":
        raise SendmailError("Wrong Sendgrid HTTP code : %s (%s)" % (response.status_code, response.body))

    return "success"