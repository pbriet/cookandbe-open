
class SendmailError(Exception):
    def __init__(self, details):
        self.details = details

class MessageType(object):
    REALTIME        = 0  # Always sent
    MAIN_INFO       = 1  # Sent if user has an active account
    NEWSLETTER      = 2  # Filtered if user unsubscribe to newsletter or deactivated his account
    NOTIFICATION    = 3  # Filtered if user unsubscribe to notifications or deactivated his account
    DAILY           = 4  # Filtered if user unsusbcribe to daily reminders  or deactivated his account