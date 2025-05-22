
from django                         import forms
from common.hook                    import HookManager

from diet_mgr.controller            import assign_diet
from diet_mgr.handlers              import InvalidDietParametersException
from diet_mgr.models                import Diet

from eater_mgr.models               import Eater

from optalim.settings               import ENABLE_PUBLIC_PAYMENT

from nutrient.models                import NutrientPack

from paybox.models                  import Subscription

from planning_mgr.controller.meta   import reset_metaplanning

from profile_mgr.controller         import set_profile_metrics, InvalidProfileValue
from profile_mgr.models             import Profile

from recipe_mgr.models              import Ustensil

from user_mgr.auth                  import authenticate, update_user_subscription_level
from user_mgr.controller.promo_code import get_promotional_code_or_none
from user_mgr.helpers               import create_user_sponsorship_code
from user_mgr.models                import User

from datetime                       import datetime, timedelta, date

import random

class UserControllerException(Exception):
    def __init__(self, title, content, **kargs):
        Exception.__init__(self, **kargs)
        self.title = title
        self.content = content

def check_email(email, check_existing=True):
    if email is None or len(email) == 0:
        raise UserControllerException("Information manquante", "L'adresse email n'a pas été spécifiée")
    f = forms.EmailField()
    try:
        f.clean(email)
    except forms.ValidationError as e:
        raise UserControllerException("Adresse e-mail invalide", "L'adresse email n'est pas valide")

    if check_existing and User.objects.filter(email = email).count():
        raise UserControllerException("Compte existant", "Il existe déjà un compte pour cette adresse e-mail")

def get_reset_code():
    # Génération d'un code de récupération de mot de passe
    nbDigits = 24
    return "".join(random.choice('0123456789ABCDEF') for i in range(nbDigits))

def do_change_settings(user, first_name, last_name):
    user.first_name = first_name
    user.last_name  = last_name
    user.save()

def do_change_login(user, email):
    # Avoid invalid mails and collisions
    if email != user.email:
        check_email(email)
    else:
        return
    user.email      = email
    # Todo: envoyer un mail de changement de login à l'ancienne adresse email avec lien d'annulation (limité dans le temps)
    user.save()

def do_reset_password(reset_operation, new_password):
    reset_operation.user.set_password(new_password)
    reset_operation.user.save()
    reset_operation.used = True
    reset_operation.save()

class PasswordException(UserControllerException):
    def __init__(self, message, **kargs):
        UserControllerException.__init__(self, "", message, **kargs)

def is_valid_password(password):
    # Todo: voir où mettre ce réglage
    min_password_length = 5
    if password is None:
        return "Aucun mot de passe spécifié"
    if len(password) < min_password_length:
        return "Le mot de passe est trop court (%i caractères minimum)" % min_password_length
    return None

def do_change_password(user, data):
    # Ancien world
    if "old_password" not in data:
        raise PasswordException("Votre ancien mot de passe n'a pas été spécifié")
    old_password = data["old_password"]
    if not user.check_password(old_password):
        raise PasswordException("Votre ancien mot de passe est incorrect")
    # New world
    if "new_password" not in data:
        raise PasswordException("Votre nouveau mot de passe n'a pas été spécifié")
    new_password = data["new_password"]
    error_message = is_valid_password(new_password)
    if error_message is not None:
        raise PasswordException(error_message)
    # Changing password
    user.set_password(new_password)
    # Todo: envoyer un mail de changement de mot de passe au client avec lien d'annulation (limité dans le temps)
    user.save()

def init_default_enabled_nutrients(user):
    """
    Enable the default nutrients
    """
    nut_pack_keys = ('default',)
    nut_packs = list(NutrientPack.objects.filter(key__in=nut_pack_keys))
    user.nutrient_packs.add(*nut_packs)


def _end_signup(user, profile, email, password):
    # Adding default ustensils
    for ustensil in Ustensil.objects.filter(default_check = True):
        user.ustensils.add(ustensil)
    # Main profile
    user.main_profile = profile
    user.save()
    # Creating a eater : this profile will be by default attending at every meals
    Eater.objects.create(user = user, profile = profile, regular = True)

    init_default_enabled_nutrients(user)

    # Creating a first metaplanning and a planning for this week
    reset_metaplanning(user)
    if not ENABLE_PUBLIC_PAYMENT and not user.is_staff:
        # Free 6-month Gold subscription when payment is not enabled
        Subscription.objects.create(level=2, user=user,
                                    nb_months=6,
                                    start_date=date.today(),
                                    end_date=date.today() + timedelta(days=6*30),
                                    trial_period_end=date.today() - timedelta(days=1), # No trial period
                                    total_amount=0,
                                    enabled=True)

    HookManager.on_new_user(user, profile)
    if password:
        # Authentication before login
        user = authenticate('public', username = email, password = password)
        assert user is not None, "Authentication failed at signup : username=<%s> password=<%s>" % (email, password)
    return user

def build_user_profile(email, password, first_name, last_name, sex=None, birth_date=None,
                       diet=None, diet_parameters=None, profile_metrics=None, promo_code=None):
    """
    Build a user and its profile
    """
    if sex is None:
        # Ugly: sexe par défaut
        sex = "female"
    # Creating the user  (login/password)
    user = User.objects.create_user(email, password, first_name=first_name, last_name=last_name)

    # Check promotional code
    if promo_code is not None:
        promo_code_obj = get_promotional_code_or_none(promo_code)
        if promo_code_obj is None:
            raise UserControllerException("Code parrainage invalide",
                                          "Ce code n'existe pas")
        elif promo_code_obj.users_who_consumed.count() > 10:
            raise UserControllerException("Code parrainage invalide",
                                          "10 parrainages ont déjà été effectués avec ce code")
        else:
            user.promotional_codes.add(promo_code_obj)
            create_user_sponsorship_code(user, "PREMIUM", datetime(2016, 7, 1), datetime(2016, 7, 1))
            update_user_subscription_level(user)

    # Creating its profile, and attaching it to the user
    profile = Profile.objects.create(creator=user, nickname=first_name, birth_date=birth_date, sex=sex)

    user = _end_signup(user, profile, email, password)

    if profile_metrics is not None:
        try:
            set_profile_metrics(profile, profile_metrics)
        except InvalidProfileValue as e:
            raise UserControllerException("Valeur de profil invalide", str(e))
    if diet is None:
        diet = Diet.objects.get(key="balanced")
        default = True
    else:
        default = False

    try:
        assign_diet(user, diet, diet_parameters, default=default)
    except InvalidDietParametersException as e:
        raise UserControllerException("Erreur de configuration", str(e))

    return user

def do_signup(email, password, first_name, last_name = "", diet=None,
              diet_parameters=None, profile_metrics=None, promo_code=None):
    """
    Try to sign up with the minimum posted data
    """
    if email:
        email = email.strip().lower()
    # Checking email
    check_email(email)
    # Checking password
    error_message = is_valid_password(password)
    if error_message is not None:
        raise PasswordException(error_message)
    password = password.strip()
    if first_name is None or len(first_name) == 0:
        raise UserControllerException("Information manquante", "Vous n'avez pas renseigné votre prénom")
    if len(email) > 74:
        raise UserControllerException("Adresse email trop longue", "L'adresse email doit avoir moins de 75 caractères")
    first_name = first_name.strip()
    last_name = last_name.strip()
    if len(first_name) > 30:
        first_name = first_name[:30]
    if len(last_name) > 30:
        last_name = last_name[:30]

    return build_user_profile(email, password, first_name, last_name, "female",
                              diet=diet, diet_parameters=diet_parameters,
                              promo_code=promo_code, profile_metrics=profile_metrics)
