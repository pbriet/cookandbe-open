from common.hook        import HookManager
from cookandbe.user     import first_visit_poll_mail, welcome_mail

# Send a "welcome" email when user just subscribed
HookManager.register_on_new_user(welcome_mail)

# Send a poll two weeks after user has subscribed
HookManager.register_on_new_user(first_visit_poll_mail)