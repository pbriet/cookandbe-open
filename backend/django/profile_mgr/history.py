from django.dispatch            import receiver
from django.db.models.signals   import post_save
from django.utils               import timezone

from common.date                import today_aware

from profile_mgr.models         import Profile, ProfileMetric, ProfileValue

@receiver(post_save, sender=Profile)
def post_profile_save(sender, instance, **kwargs):
    """
    Each time a profile is saved, we store the historified values into ProfileMetric values
    """
    for history_field, options in Profile.HISTORY_FIELDS.items():
        round_nb = options.get("round", 0)
        value = getattr(instance, history_field)
        if value is None:
            continue
        value = round(value, round_nb)
        metric = ProfileMetric.objects.get(key=history_field)
        
        # If there is a value on this metric, that has been stored the same day, remove it
        ProfileValue.objects.filter(profile=instance, time__gte=today_aware(),
                                    metric=metric).delete()
        
        if not options.get('save_if_value_is_same', True) and not has_value_changed(instance, metric, value, round_nb):
            # Value has not been modified
            continue
        
        # Create the new metric
        ProfileValue.objects.create(profile=instance, metric=metric,
                                    float_value=value, time=timezone.now(),
                                    auto_create_from_profile=True)


def has_value_changed(profile, metric, new_value, round_nb):
    """
    Check if new_value is different from last value on this metric
    """
    try:
        previous_value = ProfileValue.objects.filter(profile=profile, metric=metric).order_by('-time')[0]
    except IndexError:
        return True # No values in history
    return round(previous_value.float_value, round_nb) != new_value
