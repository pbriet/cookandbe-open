import os
from optalim.log import logger

from django.conf import settings

def campfire_message(msg, type_message="TextMessage"):
    """
    Send a message in campfire
    """
    if settings.DEBUG:
        logger.info("Campfire message : %s" % msg)
        return
    try:
        cmd = 'curl -u %s:x -H"Content-Type: application/json"' + \
            ' -d\'{"message": {"type": "%s","body": ' + \
            '"%s" }}\' %s >/dev/null 2>/dev/null'
        os.system(cmd % (settings.CAMPFIRE_MRO_KEY, type_message, msg, settings.CAMPFIRE_MAIN_ROOM))
    except Exception as e:
        logger.warning("Campfire message failed : %s" % e)