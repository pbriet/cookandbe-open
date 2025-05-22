from django.urls               import re_path

from paybox.views                   import pay_via_paybox, payment_accepted, payment_cancelled, payment_error,\
                                           payment_refused, payment_validated, api_tariffs
from paybox.views                   import api_activate_free_trial

from django.conf                    import settings

if not settings.ENABLE_PUBLIC_PAYMENT:
    urlpatterns = []
else:
    urlpatterns = [

        re_path(r'^payment/pay/$',                      pay_via_paybox),
        re_path(r'^payment/accepted/$',                 payment_accepted),  # Paybox redirection page
        re_path(r'^payment/refused/$',                  payment_refused),   # Paybox redirection page
        re_path(r'^payment/cancelled/$',                payment_cancelled), # Paybox redirection page
        re_path(r'^payment/error/$',                    payment_error),     # Paybox redirection page
        re_path(r'^op-paybox-validation/$',             payment_validated), # Called by E-transaction, through PHP. Not served to the outside world directly.

        # re_path(r'^secure/api/resiliate/$',             api_resiliate), # Only exposed in secure  --  not available anymore to the public
        re_path(r'^api/tariffs/$',                      api_tariffs),
        re_path(r'^api/user/(?P<user_id>\d+)/activate_free_trial',          api_activate_free_trial),
    ]