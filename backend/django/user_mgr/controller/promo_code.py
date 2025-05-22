from user_mgr.models        import PromotionalCode
from django.utils           import timezone

def get_promotional_code_or_none(promotional_code):
    """
    Returns a promotional code object from its code, or None if :
    - does not exists
    - is not activated anymore
    """
    if promotional_code is None:
        return None
    try:
        return PromotionalCode.objects.get(code__iexact=promotional_code, can_be_activated_until__gte=timezone.now())
    except PromotionalCode.DoesNotExist:
        return None
