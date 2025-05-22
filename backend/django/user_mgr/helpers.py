from user_mgr.models        import PromotionalCode, User
import random
import string


def create_user_sponsorship_code(user, benefit, can_be_activated_until, benefit_until):
    """
    From a given user, create a sponsorship code that he may share
    """
    user_with_codes = User.objects.filter(sponsorship_code__isnull=False).select_related('sponsorship_code')
    user_codes = [u.sponsorship_code.code for u in user_with_codes]
    is_unique = False
    while not is_unique:
        code = "".join(random.choice(string.ascii_uppercase) for i in range(9))
        code = code[:3] + "-" + code[3:6] + "-" + code[6:]
        if code not in user_codes:
            break

    code_obj = PromotionalCode.objects.create(code=code, name=user.email,
                                   benefit=benefit, can_be_activated_until=can_be_activated_until,
                                   benefit_until=benefit_until)

    user.sponsorship_code = code_obj
    user.save()
