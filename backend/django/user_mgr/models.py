
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser
from django.db                  import models
from django.utils               import timezone

from common.model               import NamedModel
from common.date                import today, get_month_range

from diet_mgr.models            import Diet

from location_mgr.models        import Address

from optalim.settings           import DEFAULT_EMAIL_DAILY, DEFAULT_EMAIL_SUGGESTION, DEFAULT_EMAIL_NEWSLETTER

import datetime
import uuid

class UserObjectsManager(BaseUserManager):
    """
    A class managing our own user class
    """
    def create_user(self, email, password=None, first_name=None, last_name=None, **kargs):
        if not email:
            raise ValueError('Users must have an email address')

        if first_name is None:
            first_name = ""
        if last_name is None:
            last_name = ""

        user = self.model(
            email=self.normalize_email(email),
            first_name=first_name,
            last_name=last_name,
            **kargs
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, *args, **kargs):
        user = self.create_user(*args, **kargs)
        user.user_roles.create(role_id = Role.R_ADMIN, created_by = user)
        user.save(using=self._db)
        return user


class UserQuestionQuota(object):
    MAX_PREMIUM_QUESTIONS_PER_MONTH = 5
    start_date  = property(lambda s: s.month_range[0])
    end_date    = property(lambda s: s.month_range[1])

    def __init__(self, user):
        self.user           = user
        self.max_questions  = 0
        self.month_range    = get_month_range()
        min_dt = timezone.make_aware(datetime.datetime.combine(self.month_range[0], datetime.datetime.min.time()), timezone.get_default_timezone())
        max_dt = timezone.make_aware(datetime.datetime.combine(self.month_range[1], datetime.datetime.max.time()), timezone.get_default_timezone())
        self.question_count = user.discussions.filter(creation_date__gte=min_dt, creation_date__lte=max_dt).count()
        if user.current_subscription is not None and user.current_subscription.level > 0:
            self.month_range = (
                max(self.month_range[0], user.current_subscription.start_date),
                min(self.month_range[1], user.current_subscription.end_date)
            )
            self.max_questions = self.MAX_PREMIUM_QUESTIONS_PER_MONTH

    def serialize(self):
        exported = ("start_date", "end_date", "max_questions", "question_count")
        return dict((key, getattr(self, key)) for key in exported)

class BaseUser(AbstractBaseUser):
    """
    Own user class
    """
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['password']

    first_name      = models.CharField('first name', max_length=30, blank=True)
    last_name       = models.CharField('last name', max_length=30, blank=True)
    email           = models.EmailField('email address', blank=True, unique=True)
    main_address    = models.ForeignKey(Address, models.SET_NULL, null = True, blank = True, related_name = "user")

    creation_date   = property(lambda user: user.date_joined)
    date_joined     = models.DateTimeField('date joined', default=timezone.now)

    facebook_id     = models.CharField(max_length=30, blank=True)

    mail_notifications  = models.BooleanField(default=True) # Does a user receive email notifications ?
    mail_newsletter     = models.BooleanField(default=DEFAULT_EMAIL_NEWSLETTER) # Does a user receive the newsletter ?
    mail_daily          = models.BooleanField(default=DEFAULT_EMAIL_DAILY) # Does a user receive daily reminders
    mail_suggestion     = models.BooleanField(default=DEFAULT_EMAIL_SUGGESTION) # Does a user receive 3xweekly suggestions ?

    # Custom privileges
    @property
    def is_admin(self):     return self.user_roles.filter(user_id = self.id, role_id = Role.R_ADMIN).count() > 0
    @property
    def is_author(self):    return self.user_roles.filter(user_id = self.id, role_id = Role.R_AUTHOR).count() > 0
    @property
    def is_moderator(self): return self.user_roles.filter(user_id = self.id, role_id = Role.R_MODERATOR).count() > 0
    @property
    def is_reviewer(self):  return self.user_roles.filter(user_id = self.id, role_id = Role.R_REVIEWER).count() > 0
    @property
    def is_operator(self):  return self.user_roles.filter(user_id = self.id, role_id = Role.R_OPERATOR).count() > 0
    @property
    def is_developer(self): return self.user_roles.filter(user_id = self.id, role_id = Role.R_DEVELOPER).count() > 0
    @property
    def is_dietician(self): return self.user_roles.filter(user_id = self.id, role_id = Role.R_DIETICIAN).count() > 0

    ## REQUIRED FOR DJANGO ADMIN

    @property
    def is_staff(self):     return self.user_roles.filter(user_id = self.id).count() > 0
    @property
    def is_superuser(self): return self.is_admin
    @property
    def is_active(self):    return True

    def has_module_perms(self, *args, **kargs):     return self.is_admin
    def has_perm(self, *args, **kargs):             return self.is_admin

class User(BaseUser):
    """
    Own user class
    """
    class Meta:
        verbose_name = 'user'
        verbose_name_plural = 'users'

    objects     = UserObjectsManager()

    # Planning template for this user
    meta_planning   = models.ForeignKey('planning_mgr.MetaPlanning',
                                        models.SET_NULL,
                                        null = True, blank = True,
                                        related_name = "+")
    shopping_day    = models.IntegerField(default = 6, null = False) # Les courses sont faites le samedi par défaut
    main_profile    = models.ForeignKey('profile_mgr.Profile',
                                        models.SET_NULL,
                                        default = None, null = True) # Profil principal associé au compte utilisateur

    ustensils           = models.ManyToManyField("recipe_mgr.Ustensil")
    completed_stages    = models.ManyToManyField("ConfigStage", through = 'ConfigStageCompletion')

    budget              = models.IntegerField(default = 2)
    meat_level          = models.IntegerField(default = 2)
    fish_level          = models.IntegerField(default = 2)

    diet                = models.ForeignKey("diet_mgr.Diet", models.SET_NULL, null=True)
    diet_changed_at     = models.DateTimeField('date joined', null=True, blank=True)

    nutrient_packs      = models.ManyToManyField('nutrient.NutrientPack')

    enabled             = models.BooleanField(default=True) # Disabled when a user ask to : no more emails

    access_closed       = models.BooleanField(default=False) # Access closed by Cook&Be or other provider

    biodymanager_id     = models.CharField(max_length=64, null=True)

    # Consumed promotional codes
    promotional_codes   = models.ManyToManyField("user_mgr.PromotionalCode", related_name="users_who_consumed")

    # Code for sponsorship
    sponsorship_code    = models.ForeignKey("user_mgr.PromotionalCode", models.SET_NULL, null=True,
                                            related_name='+')

    subscription_level  = models.IntegerField(default=0)    # This is kind of a cached value of the last user subscription level, for performances issues

    # Properties
    sex                 = property(lambda user: None if user.main_profile is None else user.main_profile.sex)

    @property
    def is_active(self):    return not self.access_closed

    def free_trial_in_progress(self):
        subscription = self.current_subscription
        return subscription is not None and subscription.total_amount == 0 and not\
            self.user.is_staff

    def get_short_name(self):
        return self.first_name

    def get_full_name(self):
        res = self.first_name[0].upper() + self.first_name[1:]
        if len(self.last_name):
            res += " " + self.last_name.upper()
        return res

    def has_promo_code_benefit(self, value):
        """
        Returns True if the user has a promotional code activated, and its effect is still valid
        """
        for promo_code in self.promotional_codes.all():
            if promo_code.benefit == value:
                return promo_code.benefit_until > timezone.now()
        return False

    @property
    def diet_handler(self):
        if hasattr(self, '_diet_handler'):
            return self._diet_handler
        diet_id = self.activated_diet.id
        self._diet_handler = Diet.get_cached(diet_id).handler(self.main_profile)
        return self._diet_handler

    @property
    def activated_diet(self):
        if self.diet is None or self.diet.get_min_subscription_level() > self.subscription_level:
            return Diet.objects.get(key="balanced")
        return self.diet

    @property
    def current_subscription(self):
        subscriptions = self.subscriptions.filter(start_date__lte = today(), end_date__gte = today(), cancelled = False, enabled = True).order_by('-id')
        if len(subscriptions) == 0:
            return None
        # Priority given to the last subscription created
        return subscriptions[0]

    @property
    def current_subscription_id(self):
        return self.current_subscription.id if self.current_subscription is not None else None

    @property
    def recent_not_nows(self):
        return self.not_nows.filter(created_at__gt=timezone.now() - datetime.timedelta(days=30))

    @property
    def question_quota(self):
        return UserQuestionQuota(self)


class AutologinToken(models.Model):
    """
    Tokens to auto-login (with temporary validity)
    """
    user        = models.ForeignKey(User, models.CASCADE)
    token       = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    created_at  = models.DateTimeField(auto_now_add = True)
    valid_until = models.DateTimeField()

    def is_valid(self):
        return timezone.now() < self.valid_until


#### OBSOLETE
class ProUser(BaseUser):
    """
    Users for access to the pro website
    """
    objects     = UserObjectsManager()

class UserOperation(models.Model):
    user          = models.ForeignKey(BaseUser, models.CASCADE)
    date          = models.DateTimeField(auto_now_add = True)
    operation     = models.CharField(max_length = 16)
    ip            = models.CharField(max_length = 32)
    used          = models.BooleanField(default = False)
    key           = models.CharField(max_length = 32, unique = True)

class ConfigStage(NamedModel, models.Model):
    """
    Configuration stage that a user has to complete
    """
    name                = models.TextField()
    express_description = models.TextField()
    description         = models.TextField()
    key                 = models.CharField(max_length=20)
    order               = models.IntegerField(null = False)
    validity_days       = models.IntegerField(default = None, null = True, blank = True)

class ConfigStageCompletion(models.Model):
    """
    Storage of configuration stage completion
    """
    user   = models.ForeignKey(User, models.CASCADE, related_name="config_stage_completions")
    stage  = models.ForeignKey(ConfigStage, models.CASCADE)
    date   = models.DateTimeField(auto_now_add=True)

    # Only 1 ConfigStageCompletion per couple stage/user
    class Meta:
        unique_together = ("user", "stage")

    def is_expired(self):
        return self.stage.validity_days is not None and\
               self.date < timezone.now() - datetime.timedelta(days=self.stage.validity_days)

    expired = property(is_expired)

class Role(models.Model):
    name            = models.CharField(max_length = 32, unique = True, blank = True)
    description     = models.TextField()

    R_ADMIN         = 1
    R_AUTHOR        = 2
    R_MODERATOR     = 3
    R_REVIEWER      = 4
    R_OPERATOR      = 5
    R_DEVELOPER     = 6
    R_DIETICIAN     = 7

class BaseUserRole(models.Model):
    user            = models.ForeignKey(BaseUser, models.CASCADE, related_name = "user_roles")
    role            = models.ForeignKey(Role, models.CASCADE)
    created_by      = models.ForeignKey(BaseUser, models.CASCADE, related_name = "promotions")
    creation_date   = models.DateTimeField(auto_now_add = True)

    class Meta:
        unique_together = ("user", "role")


class PromotionalCode(models.Model):
    """
    Promotional code allowing some limited subscriptions to the service
    """
    code            = models.CharField(max_length=40, primary_key=True) # The code the user should enter
    name            = models.CharField(max_length=100)                  # Where it comes from (name)
    url             = models.CharField(max_length=100, null=True)       # Where it comes from (URL)
    benefit         = models.CharField(max_length=10)                   # What is the benefit of the short code
    can_be_activated_until = models.DateTimeField()                     # Date until the code can be consumed
    benefit_until   = models.DateTimeField()                            # Date when the effect of the code stops

