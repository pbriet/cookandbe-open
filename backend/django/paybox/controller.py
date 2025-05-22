from django.conf                import settings

from common.date                import seconds_from_midnight, today_aware, today, add_days, add_months

from emailing                   import MessageType
from emailing.tools             import sendmail_template

from paybox.models              import Transaction, Subscription
from paybox.prices              import get_prices_and_discount

from optalim.log import logger

def update_transaction_from_getparams(transaction, params, save=False, should_be_stable=False):
    """
    Updates a transaction object from GET parameters (synchronicity of bank data and our DB)
    @param save: will call transaction.save()
    @param should_be_stable: will log some errors if some theoretically-stable data has changed
    """
                  # Database parameter,     # GET parameter,   # type of value,  # Optional
    parameters = [('transaction_id',        'trans',           int,              False),
                  ('payment_type',          'payment',         str,              True),
                  ('price',                 'amount',          int,              True),
                  ('authorization_code',    'auto',            str,              True)]

    for db_parameter, get_parameter, type_of_value, optional in parameters:

        value = params.get(get_parameter, None)
        if value is None:
            if not optional:
                logger.critical("missing info in GET parameters : %s " % get_parameter)
            continue

        value = type_of_value(value)
        splitted_db_parameters = db_parameter.split('.')
        if len(splitted_db_parameters) > 1:
            assert len(splitted_db_parameters) == 2, "not handled : sub sub parameters of transaction"
            object_to_update = getattr(transaction, splitted_db_parameters[0])
            db_parameter = splitted_db_parameters[1]
        else:
            object_to_update = transaction

        if should_be_stable:
            existing_value = getattr(object_to_update, db_parameter)
            if existing_value is not None and value != existing_value:
                logger.critical("transaction value has changed. %s :  %s  -->  %s" % (get_parameter, existing_value, value))

        setattr(object_to_update, db_parameter, value)

        if len(splitted_db_parameters) > 1 and save:
            object_to_update.save()

    if save:
        transaction.save()

def send_transaction_email(transaction):
    """
    Send an email to the user, saying that the transaction has been sucessful (or not)
    """
    template_vars = {'date': transaction.created_at,
                     'payment_details': {'N° transaction': str(transaction.transaction_id),
                                         'Référence': transaction.ref,
                                         'Prix': '%s euros' % (float(transaction.price) / 100),
                                         'Durée': "%i jours" % transaction.subscription.total_days,
                                         'Date de fin': transaction.subscription.end_date.strftime("%d/%m/%Y")}
                     }

    if transaction.status == Transaction.STATUS_CONFIRMED:
        sendmail_template(MessageType.REALTIME, 'paybox/templates/payment_success.html', template_vars,
                            "Votre commande a bien été prise en compte", users = [transaction.subscription.user],
                            tags=['payment_success'])
    else:
        template_vars['payment_details']['Code erreur'] = transaction.error_code
        template_vars['payment_details']['Statut de la transaction'] = transaction.status
        if transaction.authorization_code:
            template_vars['payment_details']['Code d\'autorisation'] = transaction.authorization_code
        sendmail_template(MessageType.REALTIME, 'paybox/templates/payment_failure.html', template_vars,
                            "Votre commande a échoué", users = [transaction.subscription.user],
                            tags=['payment_failed'])

# def send_unsubscribed_email(transaction):
#     """
#     Send an email to the use saying that his subscription is resiliated
#     """
#     template_vars = {'transaction_ref': transaction.ref}

#     sendmail_template(MessageType.REALTIME, 'paybox/templates/resiliation.html', template_vars,
#                         "Votre abonnement a été résilié", users = [transaction.subscription.user],
#                         tags=['resiliation'])

def activate_premium(subscription):
    """
    Activate the user subscription
    """
    subscription.enabled = True
    subscription.save()
    subscription.user.subscription_level = subscription.level
    subscription.user.save()

def disable_premium(subscription, bank_failure=True):
    """
    Disable the user subscription
    """
    subscription.cancelled = True
    if bank_failure:
        subscription.enabled = False
    subscription.save()
    subscription.user.subscription_level = 0
    subscription.user.save()

def check_payment_success(request, transaction):
    """
    Check that the content of request reflects a successful bank payment
    # - authorization number 'auto' must be not empty
    # - error code should be '00000'
    # - the amount should be the one expected
    """
    if transaction.error_code > 0:
        if transaction.error_code in (30,):
            return Transaction.STATUS_CANCELLED
        if transaction.error_code in (4, 8, 21, 29, 33) or transaction.error_code > 100:
            return Transaction.STATUS_REFUSED
        return Transaction.STATUS_ERROR
    if 'auto' not in request.GET or request.GET['auto'] == '':
        return Transaction.STATUS_ERROR
    if 'amount' not in request.GET or int(request.GET['amount']) != transaction.price:
        return Transaction.STATUS_WRONG_AMOUNT
    return None

# The paybox procedure is the following : we ask a question, they answer
# A unique question number is required (unique for one day)
# We do the following : seconds from 00:00 (5 digits) + user_id (last 5 digits)
# Warning : a conflict 'might' happen (very unlikely but... it can)
def gen_pps_num_question(user_id, additional_seconds=0):
    res = '1%#05i' % (seconds_from_midnight() + additional_seconds)
    return res + '%#04i' % (user_id % 10000)


# def pps_paybox_call(call_type, user_id, amount, ref, trans_date=None, num_trans=None, num_appel=None, call_number=0):
#     """
#     Calls paybox PPS service.
#     Returns None in case of failure (add a critical log)
#     Returns the dictionnary of response values in case of success
#     @param call_number: if there is more than one call to PPS in your flow, increase call_number (0, then 1, then 2...)
#     """
#     if trans_date is None:
#         trans_date = timezone.now()
#     num_question = gen_pps_num_question(user_id, call_number)
#     # Ugly ugly on paybox : it crashes when RANG is the first parameter to be sent.
#     # This is why we cannot give a dictionnary to the requests library : the order would be random.
#     # We MUST pass a querystring that starts with REFERENCE.
#     # Yup, that's how life is with Paybox...
#     querystring = "REFERENCE=" + ref
#     params = {'VERSION': '00104', 'TYPE': call_type, 'SITE': settings.PBX_SITE, 'RANG': settings.PBX_RANG,
#               'DATEQ': trans_date.strftime('%d%m%Y%H%M%S'), 'NUMQUESTION': num_question,
#               'CLE': settings.PBX_BACKEND_PASSWORD, #TODO
#               'MONTANT': str(amount), 'DEVISE': '978'}
#     if num_trans is not None:
#         params['NUMTRANS'] = num_trans
#     if num_appel is not None:
#         params['NUMAPPEL'] = num_appel

#     for key, value in sorted(params.items(), key=lambda x: x[0]):
#         querystring += "&" + key + "=" + value

#     r = requests.post('https://ppps.paybox.com/PPPS.php', data=querystring)
#     if r.status_code != 200:
#         logger.critical("PPS : Paybox returned an invalid status code : %s. Params : %s" % (r.status_code, params))
#         return None

#     result = parse_qs(r.text)
#     result = dict((key, val[0]) for key, val in result.items())
#     if result['CODEREPONSE'] != '00000':
#         logger.critical("PPS : Paybox returned an invalid response code : %s. Params : %s" % (r.text, params))
#         return None
#     assert num_question == result['NUMQUESTION'], "numquestion is not correct ?"
#     return result


def get_user_discount(user=None):
    """
    Returns the discount applied specifically to the user, if there is one
    """
    if user is None or user.is_anonymous:
        return 0
    offers = list(user.special_offers.filter(until__gte=today_aware()))
    if len(offers) > 0:
        return max(offer.discount for offer in offers)
    return 0

def get_user_tariffs(user=None, cents_to_euros=True):
    """
    Returns the tariffs that the user should pay,
    and the discount, if there is one
    """
    discount = get_user_discount(user)
    return get_prices_and_discount(min_discount=discount, cents_to_euros=cents_to_euros)

def get_user_best_tariff_str(user, level):
    """
    For a given user, and a given subscription level,
    returns the best price available. In str format
    """
    best_tariff = get_user_tariffs(user)
    best_tariff = best_tariff[level][12]['after_discount']
    if abs(int(best_tariff) - best_tariff) < 0.01:
        best_tariff = "%i" % int(best_tariff) # No cents
    else:
        best_tariff = "%.2f" % best_tariff # With cents
    return best_tariff


def create_subscription(user, level, nb_months=0, nb_days=0, price=0, trial_days=-1):
    assert nb_days + nb_months > 0

    start_date = today()
    end_date = today()
    if nb_months > 0:
        end_date = add_months(end_date, nb_months)
    if nb_days > 0:
        end_date = add_days(end_date, nb_days)

    # Creating a new subscription
    trial_period_end    = add_days(today(), trial_days)

    subscription = Subscription.objects.create(level=level, user=user, start_date=start_date, end_date=end_date,
                                               trial_period_end=trial_period_end, total_amount=price,
                                               enabled=(price == 0), nb_months=nb_months,
                                               nb_days=nb_days, cancelled=False, discount=None)
    return subscription