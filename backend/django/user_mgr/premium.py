
from rest_framework.response    import Response

from functools                  import update_wrapper

def requires_premium_response():
    return Response({'status': 'error', 'error': 'requires_premium'}, 200)
    
def ensure_subscription_level(min_level):
    """
    Decorator of a view which requires a minimum level of user subscription.
    Returns {'status': 'error', 'error': 'requires_premium'} if level is not high enough (with HTTP code 200)
    """
    def decorator(fcn):
        def new_fcn(request, *args, **kargs):
            if request.user.subscription_level < min_level:
                return requires_premium_response()
            return fcn(request, *args, **kargs)
        update_wrapper(new_fcn, fcn)
        return new_fcn
    return decorator
