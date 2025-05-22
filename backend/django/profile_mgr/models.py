from django.db                  import models
from django.utils               import timezone
from user_mgr.models            import User

from common.model               import NamedModel
from common.date                import today
from recipe_mgr.models          import Food, FoodTag, Recipe

import datetime, math


def COMPUTE_IMC(weight, height):
    return float(weight) / (float(height) / 100) ** 2

def COMPUTE_IMC_WEIGHT(imc, height):
    return math.floor(imc * (float(height) / 100) ** 2)

class Profile(models.Model):
    """
    Personal user data (height, weight), which will be used to calculate the best food ratio
    """
    DEFAULT_AGE    = 30
    # From 0 to 18 years old
                                # 0   1   2    3   4   5   6  7   8   9   10  11  12  13  14  15  16  17  18+
    DEFAULT_WEIGHT = {"male":   [3.5, 10, 12, 15, 16, 17, 19, 21, 23, 26, 28, 32, 37, 41, 48, 54, 58, 62, 80],
                      "female": [3.5, 10, 12, 15, 16, 17, 19, 21, 23, 26, 28, 32, 37, 41, 48, 52, 55, 57, 60]}
                                # 0   1   2    3   4   5    6     7    8    9   10    11  12   13    14   15  16  17  18+
    DEFAULT_HEIGHT = {"male":   [52, 72, 85,  92,  99, 105, 111, 117, 122, 128, 134, 138, 145, 152, 160, 166, 172, 174, 180],
                      "female": [52, 72, 85,  92,  99, 105, 111, 117, 122, 128, 134, 138, 145, 150, 157, 160, 165, 170, 170]}
    DEFAULT_BLACK_CO_COEFF = {"male": 1.083, "female": 0.963}
    OVERWEIGHT_IMC = 25
    THIN_IMC = 18.5
    MENOPAUSE_EFFECT = 0.9 # applied to metabolism

    creator             = models.ForeignKey(User, models.CASCADE, default = None, null = True)
    nickname            = models.CharField(max_length = 64)
    creation_date       = models.DateTimeField(auto_now_add=True, blank=True)
    modification_date   = models.DateTimeField(auto_now_add=True, blank=True)
    weight              = models.FloatField(null=True, blank=True) # In kilograms (kg)
    height              = models.IntegerField(null=True, blank=True) # In centimeters (cm)

    # How the user burns its calories 0 to 6
    work_score          = models.IntegerField(null=True, blank=True) # At work
    moving_score        = models.IntegerField(null=True, blank=True) # By moving (by foot, bicycle, ..)
    sport_score         = models.IntegerField(null=True, blank=True) # By doing some sports

    # TODO: change this to a date
    birth_date          = models.DateTimeField(default=None, null=True, blank=True)
    sex                 = models.CharField(max_length = 20)  # Male or female
    metabolism          = models.FloatField(default=1.0) # Correcting quantities depending on metabolism.
                                                         # metabolism > 1, needs more food to maintain weight
                                                         # metabolism < 1, needs to reduce the amount of calories
    # pathologies         = models.ManyToManyField(Pathology)

    # If non-null, these calories are used instead of a calculation based on age/height/weight
    forced_base_calories = models.IntegerField(null=True)


    # History field names and options  (defaults: round=0, save_if_value_is_same=True)
    # cf history.py
    HISTORY_FIELDS = {'weight': {'round': 1},
                      'height': {},
                      'metabolism': {'round': 6, 'save_if_value_is_same': False}}

    NAP_POINTS_TO_SCORE = {0: 1.3, 1: 1.4, 2: 1.5, 3: 1.6, 4: 1.6, 5: 1.6, 6: 1.7, 7: 1.7, 8: 1.8}

    @property
    def nap_score(self):
        """
        Physical activity
        """
        work_score   = self.work_score   if self.work_score   is not None else 1
        moving_score = self.moving_score if self.moving_score is not None else 1
        nap_points = min(8, work_score + moving_score + (self.sport_score or 0))
        assert nap_points in self.NAP_POINTS_TO_SCORE, "Invalid total nap_points : %s" % nap_points
        return self.NAP_POINTS_TO_SCORE[nap_points]


    @property
    def age(self):
        if (self.birth_date is None):
            return self.DEFAULT_AGE
        today_value = today()
        age = today_value.year - self.birth_date.year
        if (today_value.month, today_value.day) < (self.birth_date.month, self.birth_date.day):
            age -= 1
        return age

    @property
    def imc(self):
        return COMPUTE_IMC(self.weight_or_default, self.height_or_default)

    @property
    def imc_caption(self):
        imc = self.imc
        if imc < self.THIN_IMC:
            return "maigreur"
        if imc > self.OVERWEIGHT_IMC:
            return "surpoids"
        return "normal"

    @property
    def is_main_profile(self):
        if self.creator is None:
            return True
        return self.creator.main_profile == self

    def _get_last_measure(self, key, value_only=True):
        val = self.values.filter(key=key).order_by('-time').next()
        if value_only:
            return val.float_value
        return val

    @property
    def weight_or_default(self):
        if self.weight is not None:
            return self.weight

        return self.DEFAULT_WEIGHT[self.sex][min(self.age, 18)]

    @property
    def height_or_default(self):
        if self.height is not None:
            return self.height
        return self.DEFAULT_HEIGHT[self.sex][min(self.age, 18)]

    def history_values(self, key, min_date=None, max_date=None):
        """
        Return the history of one float value, [(date, value), (date, value)]
        sorted by date ascending
        """
        assert key in self.HISTORY_FIELDS, "%s is not in HISTORY_FIELDS" % key
        query = ProfileValue.objects.filter(metric__key=key, profile=self)
        if min_date is not None:
            query = query.filter(time__gte=min_date)
        if max_date is not None:
            query = query.filter(time__lte=max_date)
        res = []
        for value in query.order_by('time'):
            res.append((value.time, value.float_value))
        return res

    # From official ANC docs (average NAP)
    YOUNG_CHILDREN_MJ_PER_DAY = {
        "male": {2: 4.8, 3: 5.1, 4: 5.6, 5: 6.0, 6: 7.3, 7: 7.8, 8: 8.3, 9: 8.8},
        "female": {2: 4.4, 3: 4.8, 4: 5.2, 5: 5.7, 6: 6.7, 7: 7.2, 8: 7.7, 9: 8.2},
    }

    def _child_caloric_need(self, age):
        """
        Caloric need calculation for children
        """
        age = max(age, 2)
        if age <= 9:
            # MJ * 1000 / [j->kcal]  = kcal
            return self.YOUNG_CHILDREN_MJ_PER_DAY[self.sex][age] * 1000 * 0.239
        weight, height = self.weight_or_default, self.height_or_default

        if self.sex == 'male':
            # Thierry : 13/09/15
            res = (69.4 * weight + 322 * height/100 + 2392)/4.185 * self.nap_score + 50
            if weight < 55:
                res += 50
            return res
        # Thierry : 13/09/15
        # Young ladies
        res = (30.9  * weight + 2016.6 * height/100 + 907)/4.185 * self.nap_score + 30
        if weight < 55:
            res += 90
        return res

    def _adult_caloric_need(self, age, weight=None):
        """
        Caloric need calculation for adults (Black&Co)
        # Homme = [1,083 x Poids(kg)0,48 x Taille(m)0,50 x Age(an)-0,13] x (1000/4,1855)
        # Femme = [0,963 x Poids(kg)0,48 x Taille(m)0,50 x Age(an)-0,13] x (1000/4,1855)
        Multiplied by NAP
        """
        height = float(self.height_or_default)
        if weight is None:
            weight = self.weight_or_default
        imc = COMPUTE_IMC(weight, height)
        if imc > self.OVERWEIGHT_IMC:
            # Patch: prevent high-weighted profiles from having a very big ratio and a huge caloric need
            weight = self.OVERWEIGHT_IMC * (height / 100) ** 2
            imc = self.OVERWEIGHT_IMC
        elif imc < self.THIN_IMC and age >= 18:
            weight = self.THIN_IMC * (height / 100) ** 2
            imc = self.THIN_IMC

        coeff = self.DEFAULT_BLACK_CO_COEFF[self.sex]
        if age > 50 and self.sex == 'female':
            coeff *= self.MENOPAUSE_EFFECT
        value = self.nap_score * coeff * self.metabolism * pow(weight, 0.48) * pow(height / 100, 0.5) * pow(age, -0.13) * (1000/4.1855)

        # Patch by Thierry & Institut Pasteur 12/08/2015. Black&Co is slightly wrong with high IMC values
        if imc > self.THIN_IMC:
            value -= 250 * (imc - self.THIN_IMC) / (self.OVERWEIGHT_IMC - self.THIN_IMC)
        return value

    def theorical_caloric_need(self, weight=None):
        """
        Returns the theorical caloric need for the profile
        Calculated on the basis of weight/height/age/nap/...
        """
        age = self.age
        if age >= 18:
            return self._adult_caloric_need(age, weight=weight)
        return self._child_caloric_need(age)

    def caloric_need(self):
        """
        Caloric need for profile. Either calculated or provided by external sources
        """
        if self.forced_base_calories:
            # Provided by external sources
            return self.forced_base_calories * self.nap_score
        # Calculated
        return self.theorical_caloric_need()

class ProfileMetric(models.Model):
    """
    metric name that is bound to a profile
    """
    key                 = models.CharField(max_length = 32)
    name                = models.CharField(max_length = 64)
    unit                = models.CharField(max_length = 32)
    description         = models.TextField()

class _ProfileValueManager(models.Manager):
    def create(self, *args, **kargs):
        if not kargs.get('auto_create_from_profile', False):
            assert False, "creating profile values is strongly not recommended without using Profile HistoryFields"
        kargs.pop('auto_create_from_profile')
        return super().create(*args, **kargs)

class ProfileValue(models.Model):
    """
    Measures of values in time, for a profile and a given parameter
    """
    profile             = models.ForeignKey(Profile, models.CASCADE, related_name="values")
    metric              = models.ForeignKey(ProfileMetric, models.CASCADE)
    float_value         = models.FloatField()
    time                = models.DateTimeField(default=timezone.now)

    objects = _ProfileValueManager()  # Adding a specific objects manager to block objects.create() outside HistoryFields

class Taste(models.Model):
    """
    User's food fondness.

    Note: do not mistake with food intolerance or allergy.
    """
    class Meta:
        unique_together = ("profile", "food_tag")

    profile             = models.ForeignKey(Profile, models.CASCADE, related_name = 'tastes')
    food_tag            = models.ForeignKey(FoodTag, models.CASCADE, related_name = 'tastes')
    fondness            = models.IntegerField() # from -5 (dislike) to 5 (like) with a default value of 0 (neutral)

class RestrictedFood(models.Model):
    """
    Interdiction concerning a specific food tag.
    """
    class Meta:
        unique_together = ("profile", "food_tag")

    profile             = models.ForeignKey(Profile, models.CASCADE, related_name = 'restrictions')
    food_tag            = models.ForeignKey(FoodTag, models.CASCADE)

class RecipeDislike(models.Model):
    """
    When a user says that he doesn't like a given recipe
    """
    class Meta:
        unique_together = ("profile", "recipe")

    profile             = models.ForeignKey(Profile, models.CASCADE, related_name = 'recipe_dislikes')
    recipe              = models.ForeignKey(Recipe, models.CASCADE)

# class Pathology(NamedModel, models.Model):
    # """
    # User's medical condition : food intolerance, food allergy, ...
    # """
    # name                = models.CharField(max_length = 64)
    # tags                = models.ManyToManyField(FoodTag)

import profile_mgr.history # Required to enable auto-history storage on profile objects
