
from user_mgr.models            import User
from emailing.tools             import sendmail_template, MessageType

from django.conf                import settings

THIERRY = None

def _get_thierry():
    global THIERRY
    if THIERRY is None:
        THIERRY = User.objects.get(pk = 5) # Thierry Poitou
    return THIERRY

def send_new_question_email(discussion):
    dietician = discussion.dietician
    if discussion.dietician is None:
        dietician = _get_thierry()
    sendmail_template(
        MessageType.REALTIME,
        'discussion/templates/new_question.html',
        {
            'discussion_title': discussion.title,
            'discussion_id': discussion.id,
        },
        "[%s] Nouvelle question utilisateur" % settings.APP_BRAND_NAME,
        users = [dietician],
        tags = ['new_question'],
    )

def send_new_message_email(discussion):
    dietician = discussion.dietician
    if discussion.dietician is None:
        dietician = _get_thierry()
    sendmail_template(
        MessageType.REALTIME,
        'discussion/templates/new_message.html',
        {
            'discussion_title': discussion.title,
            'discussion_id': discussion.id,
        },
        "[%s] Nouveau message utilisateur" % settings.APP_BRAND_NAME,
        users = [dietician],
        tags = ['new_message'],
    )

def send_new_response_email(discussion):
    quota = discussion.owner.question_quota
    sendmail_template(
        MessageType.REALTIME,
        'discussion/templates/new_response.html',
        {
            'discussion_title': discussion.title,
            'discussion_id': discussion.id,
            'nb_month_questions': quota.question_count,
            'remaining_questions': (quota.max_questions - quota.question_count),
            'end_of_month': quota.end_date,
            'dietician_name': discussion.dietician.get_full_name(),
        },
        "[%s] " % settings.APP_BRAND_NAME + discussion.title,
        users = [discussion.owner],
        tags = ['new_response'],
    )
