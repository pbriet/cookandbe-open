from rest_framework.decorators  import api_view, permission_classes
from rest_framework.response    import Response

from django.db                  import DatabaseError, transaction
from django.utils               import timezone

from common.decorators          import api_arg, api_model_arg
from common.permissions         import Allow

from emailing.tools             import sendmail, MessageType

from newsletters.models         import Newsletter

from optalim.settings           import DEBUG, TESTING, APP_BRAND_NAME, SUPPORT_EMAIL, APP_BASE_URL

from user_mgr.models            import User

from datetime                   import datetime

# import mandrill
import re

@api_view(['GET'])
@api_arg('include_already_imported', bool, False)
@permission_classes((Allow("author"), ))
def mandrill_templates_list(request, include_already_imported):
    """
    Returns the list of recent mandrill templates
    """
    if DEBUG and not TESTING:
        return Response({"status": "error", "error": "template retrieval is deactivated in DEBUG"}, status=200)
    try:
        mandrill_client = mandrill.Mandrill(MANDRILL_API_KEY)
        templates_list = mandrill_client.templates.list()
    except mandrill.Error as e:
        return Response({"status": "error", "error": str(e)}, status=200)

    if not include_already_imported:
        already_imported = [n.template_name for n in Newsletter.objects.all()]


    res = []
    for template in templates_list:
        if not include_already_imported and template['name'] in already_imported:
            continue
        res.append({'name': template['name'],
                    'updated_at': datetime.strptime(template['updated_at'][:19], '%Y-%m-%d %H:%M:%S')})

    # Sort templates by update date
    res = sorted(res, key=lambda x: x['updated_at'], reverse=True)
    if len(res) > 10:
        res = res[:10]

    return Response({"status": "ok", "content": res}, 200)

@api_view(['POST'])
@api_arg('template_name', str)
@permission_classes((Allow("author"), ))
def mandrill_import_template(request, template_name):
    """
    Import a mandrill template into the newsletter collection
    """
    if Newsletter.objects.filter(template_name=template_name).count() > 0:
        return Response({"error": "already imported"}, 400)
    try:
        mandrill_client = mandrill.Mandrill(MANDRILL_API_KEY)
        template_infos = mandrill_client.templates.info(name=template_name)
        Newsletter.objects.create(content=clean_mailchimp(template_infos['code']),
                                  subject=template_infos['name'],
                                  template_name=template_name)
    except mandrill.Error as e:
        return Response({"error": str(e)}, status=400)

    return Response({"status": "imported"}, status=200)

def clean_mailchimp(html):
    """
    Clean HTML code retrieved from mailchimp, by replacing the variables
    """
    values = {'*|CURRENT_YEAR|*': str(datetime.now().year),
              '*|LIST:COMPANY|*': APP_BRAND_NAME,
              '*|LIST:DESCRIPTION|*': '',
              '*|HTML:LIST_ADDRESS_HTML|*': SUPPORT_EMAIL,
              '*|UNSUB|*': APP_BASE_URL, #FIXME
              '*|UPDATE_PROFILE|*': APP_BASE_URL #FIXME
    }
    for variable, value in values.items():
        html = html.replace(variable, value)

    html = re.compile('<a href="\*\|ARCHIVE\|\*" target="_blank">[\s\w]+</a>').sub('', html)
    return html

@api_view(['GET'])
@api_arg('published', bool, None)
@permission_classes((Allow("author"), ))
def newsletter_list(request, published):
    """
    Returns the list of newsletters
    """
    query = Newsletter.objects.all()
    if published is not None:
        if published:
            # Published only
            query = query.exclude(sent_at__isnull=True).exclude(sent_by__isnull=True)
        else:
            # Non-published only
            query = query.filter(sent_at__isnull=True, sent_by__isnull=True)
    query.order_by('-created_at')

    res = []
    for newsletter in query[:10]:
        res.append({'id': newsletter.id,
                    'subject': newsletter.subject,
                    'created_at': newsletter.created_at})

    return Response(res)

@api_view(['POST'])
@api_model_arg('newsletter', Newsletter)
@permission_classes((Allow("author"), ))
def newsletter_remove(request, newsletter):
    if newsletter.sent_at or newsletter.sent_by:
        return Response({"status": "error", "message": "cannot delete sent newsletters"})
    newsletter.delete()
    return Response({"status": "ok"})

@api_view(['GET'])
@api_model_arg('newsletter', Newsletter)
@permission_classes((Allow("author"), ))
def newsletter_details(request, newsletter):
    return Response({"subject": newsletter.subject,
                     "created_at": newsletter.created_at,
                     "id": newsletter.id,
                     "content": newsletter.content})

@api_view(['POST'])
@api_model_arg('newsletter', Newsletter)
@api_arg('send_at', datetime, None)
@permission_classes((Allow("author"), ))
@transaction.atomic
def newsletter_send(request, newsletter, send_at):
    """
    Send the newsletter to the userbase
    @param send_at: if None, send it immediately. Otherwise, send it ASAP once send_at is passed
    """
    # Select the newsletter again and lock the entry in the database,
    # So that nobody else can modify it
    try:
        newsletter = Newsletter.objects.select_for_update(nowait=True).get(pk=newsletter.id)
    except DatabaseError as e:
        print(str(e))
        return Response({"error": "newsletter is BEING SENT"}, status=400)

    if newsletter.sent_at is not None or newsletter.sent_by is not None:
        return Response({"error": "newsletter has already been sent !"}, status=400)
    newsletter.sent_at = timezone.now()
    newsletter.sent_by = request.user
    newsletter.save()

    users = User.objects.all().order_by('id')

    _send_newsletter(newsletter, users=users, eta=send_at)

    return Response({"status": "sent"})

def _send_newsletter(newsletter, **kargs):
    """
    Really send the newsletter !
    """
    sendmail(MessageType.NEWSLETTER, newsletter.subject, newsletter.content,
             tags=['newsletter', 'newsletter_%i' % newsletter.id], send_async=True,
             expires=24*60*60, with_bcc=False, **kargs)

@api_view(['POST'])
@api_model_arg('newsletter', Newsletter)
@permission_classes((Allow("author"), ))
def newsletter_testsend(request, newsletter):
    """
    Test the newsletter by sending it to the admin
    """
    _send_newsletter(newsletter, users=[request.user])
    return Response({"status": "sent"})
