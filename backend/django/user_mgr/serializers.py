from rest_framework             import serializers

from common.date                import today
from common.rest                import SerializerWithCustomFields

from django.utils               import timezone

from location_mgr.serializers   import AddressSerializer

from diet_mgr.serializers       import DietSerializer

from user_mgr.models            import ConfigStage, User, Role, PromotionalCode

class ConfigStageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConfigStage
        exclude = []

class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        exclude = []

class BaseUserSerializer(SerializerWithCustomFields):

    def fill_additional_data(self, user, result):
        result["userid"] = user.id
        result["username"] = user.first_name
        result["creation_date"] = user.creation_date
        result["main_address"] = user.main_address and AddressSerializer(user.main_address).data
        # TODO: factoriser
        result["is_admin"] = user.is_admin
        result["is_author"] = user.is_author
        result["is_moderator"] = user.is_moderator
        result["is_reviewer"] = user.is_reviewer
        result["is_operator"] = user.is_operator
        result["is_developer"] = user.is_developer
        result["is_staff"] = user.is_staff
        result["is_dietician"] = user.is_dietician
        # Fin TODO
        return result

class UserSerializer(BaseUserSerializer):
    class Meta:
        model = User
        fields = ("first_name", "last_name", "shopping_day", "email", "subscription_level")


    def fill_additional_data(self, user, result):
        result = super().fill_additional_data(user, result)

        result["sex"] = user.sex
        result["meta_planning_id"] = user.meta_planning_id
        result["main_profile_id"] = user.main_profile_id
        result["objective"] = DietSerializer(user.activated_diet).data
        result["diet_changed_at"] = user.diet_changed_at
        if user.diet is not None:
            result["wanted_objective"]= DietSerializer(user.diet).data
        result["ustensils"] = tuple(ustensil.id for ustensil in user.ustensils.all())
        result["subscription"] = user.current_subscription_id
        result["joined_today"] = user.creation_date.date() == timezone.now().date()

        if user.sponsorship_code is not None:
            result["sponsorship_code"] = user.sponsorship_code.code

        result["free_trial"] = {"enabled": False, "consumed": False}

        subscription = user.current_subscription
        if subscription is not None:
            result["can_resiliate"] = today() <= subscription.trial_period_end and subscription.total_amount > 0
            result["subscription_end_date"] = subscription.end_date
            result["subscription_level"] = subscription.level

            if subscription.total_amount == 0 and not result.get("is_staff", False):
                # Free trial in progress
                result["free_trial"]["enabled"] = True

        if user.subscriptions.count() > 0:
            # One free trial has been already created (or directly - one payment)
            result["free_trial"]["consumed"] = True
        return result


class PromotionalCodeSerializerWithStats(SerializerWithCustomFields):
    class Meta:
        model = PromotionalCode
        exclude = []

    def fill_additional_data(self, promo_code, result):
        result["nb_users"] = promo_code.nb_users
        return result