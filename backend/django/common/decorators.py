from django.core.exceptions import PermissionDenied, ValidationError
from django.http import HttpRequest, HttpResponse

from common.converters import convert, can_convert

from rest_framework.response import Response
from rest_framework.request import Request

from functools import update_wrapper

import datetime, time
import json
import rest_framework


def get_request_obj(args):
    """
    Retrieves in the arguments which one is the Request object
    """
    if isinstance(args[0], Request) or isinstance(args[0], HttpRequest):
        # Classic view functions
        return args[0]
    # Probably a method
    if len(args) > 1 and (isinstance(args[1], Request) or isinstance(args[1], HttpRequest)):
        return args[1]
    if hasattr(args[0], "request"):
        return getattr(args[0], "request")
    assert False, "No request detected in this function/method"


def api_arg(arg_name, arg_type=None, *default_value, is_list=False, validators=None):
    """
    Encapsulate an api function (with first argument being request)
    Retrieve argument from request.data or request.GET or existing kargs,
    and pass it in the kargs of the decorated function - once converted
    @param arg_name: expected name of the argument (in request.data / request.GET)
    @param arg_type: expected type of the argument
    @param *default_value: 3rd argument: if there is a 3rd argument, this is the default value !
                                         if not, there is no default -- a value is required
    @param is_list: expected value is a list of values of arg_type
    @param validators: list of django validators that will be applied on the value
    """
    has_default = len(default_value) > 0
    if has_default:
        assert len(default_value) == 1, "More than 1 default value specified ? Ensure that *args length is 1"
        default_value = default_value[0]

    # Creating decorator
    def decorator(fcn):
        def new_fcn(*args, **kargs):
            request = get_request_obj(args)
            user_provided = False
            dicos = [kargs, request.GET]
            if hasattr(request, "data"):
                dicos.append(request.data)
            # Extracting value from request
            for dico in dicos:
                if arg_name in dico:
                    if type(dico) is dict or not is_list:
                        arg_value = dico[arg_name]
                    else:
                        arg_value = dico.getlist(arg_name)
                    user_provided = True
                    break
            else:
                if has_default:
                    arg_value = default_value
                else:
                    return Response({"error": "missing argument %s" % arg_name}, status=400)
            # Warning: default values are not checked for validity because of user_provided. You've been warned !
            if arg_type and user_provided:
                if arg_value in ("None", None):
                    # None values are allowed only if the default value is also None
                    if not has_default or default_value is not None:
                        return Response({"error": "none is not allowed for argument %s" % arg_name}, status=400)
                    arg_value = None
                else:
                    # Checking type compatibility
                    assert can_convert(arg_type), "No converter for arg type : %s" % arg_type
                    try:
                        if is_list:
                            if type(arg_value) != list:
                                return Response({"error": "%s is not a list" % arg_name}, status=400)
                            arg_value = [convert(v, arg_type) for v in arg_value]
                        else:
                            arg_value = convert(arg_value, arg_type)
                    except ValueError:
                        return Response({"error": "invalid value for %s (wrong type)" % arg_name}, status=400)
                # Validation
                if validators is not None:
                    for validator in validators:
                        try:
                            validator(arg_value)
                        except ValidationError as v:
                            return Response({"error": "invalid value for %s (%s)" % (arg_name, v)}, status=400)
            # Final value
            kargs[arg_name] = arg_value
            return fcn(*args, **kargs)

        update_wrapper(new_fcn, fcn)
        return new_fcn

    return decorator


def api_cookie_arg(cookie_name, error_code=400, allow_none=False):
    """
    Extract a cookie value from request and inject it.
    If not available, return a response with error_code status
    """

    def decorator(fcn):
        def new_fcn(*args, **kargs):
            request = get_request_obj(args)
            cookie_value = request.COOKIES.get(cookie_name, None)
            if cookie_value is None and not allow_none:
                return Response({"status": "error", "error": "Cookie <%s> required and not set" % cookie_name}, error_code)
            kargs[cookie_name] = cookie_value
            return fcn(*args, **kargs)

        return new_fcn

    return decorator


def api_model_arg(arg_name, arg_model_type, allow_none=False, is_list=False, id_arg_name=None, pk_name=None, pk_type=None):
    assert allow_none is not None, "allow_none must be True or False, not None"
    if pk_name is None:
        pk_name = "pk"
    if pk_type is None:
        pk_type = int
    # Creating parent decorator
    if id_arg_name is None:
        if is_list:
            assert arg_name[-1] == "s", 'api_model_arg name with is_list=True should finish with an "s"'
            assert arg_name[-4:] != "_ids", "api_model_arg doesn't return ids"
            id_arg_name = arg_name[:-1] + "_ids"
        else:
            assert arg_name[-3:] != "_id", "api_model_arg doesn't return ids"
            id_arg_name = arg_name + "_id"
    args = [
        id_arg_name,
        pk_type,
    ]
    if allow_none:
        args.append(None)
    parent_decorator = api_arg(*args, is_list=is_list)

    # Creating son decorator
    def decorator(fcn):
        def new_fcn(*args, **kargs):
            if kargs[id_arg_name] is None:
                kargs[arg_name] = None
            else:
                if is_list:
                    ids = set(kargs[id_arg_name])
                else:
                    ids = set(
                        [
                            kargs[id_arg_name],
                        ]
                    )
                objects = arg_model_type.objects.filter(**{"%s__in" % pk_name: ids})
                # Checking objects count
                if len(ids) != len(objects):
                    invalid_ids = ids.difference(set(obj.id for obj in objects))
                    # print("Invalid ids for %s : %s" % (id_arg_name, str(invalid_ids)))
                    return Response({"error": "Invalid ids"}, status=400)
                if not is_list:
                    # Checking single query mode
                    if len(objects) != 1:
                        return Response({"error": "Get returned more than 1 %s" % arg_name}, status=400)
                    kargs[arg_name] = objects[0]
                else:
                    kargs[arg_name] = objects
            if id_arg_name != arg_name:
                del kargs[id_arg_name]
            return fcn(*args, **kargs)

        update_wrapper(new_fcn, fcn)
        return new_fcn

    return lambda fcn: parent_decorator(decorator(fcn))


def api_check_user_id(fcn):
    """
    Encapsulate an api function with the 2 following first arguments : request, user_id
    Ensure that request.user.id == user_id. Raises PermissionDenied otherwise
    """

    def new_fcn(*args, **kargs):
        try:
            kargs["user_id"] = int(kargs["user_id"])
        except ValueError:
            return Response({"error": "user_id is not an int"}, 400)
        request = get_request_obj(args)
        if request.user.id != kargs["user_id"]:
            raise PermissionDenied
        return fcn(*args, **kargs)

    update_wrapper(new_fcn, fcn)
    return new_fcn


def overrides(interface_class):
    """
    Asserts that this method exists in a parent
    """

    def overrider(method):
        assert method.__name__ in dir(interface_class), "Missing method in parent"
        return method

    return overrider


def rest_response_to_django_response(fcn):
    def new_fcn(*args, **kargs):
        res = fcn(*args, **kargs)
        if isinstance(res, rest_framework.response.Response):
            return HttpResponse("%s" % res.data, status=400)
        return res

    update_wrapper(new_fcn, fcn)
    return new_fcn


def print_time(fcn):
    """
    Compute execution time and print it
    """

    def new_fcn(*args, **kargs):
        start = time.perf_counter(), time.time()
        res = fcn(*args, **kargs)
        end = time.perf_counter(), time.time()
        label = fcn.__name__
        print("*** %s *** cpu %.3f s | real %.3f s" % (label, end[0] - start[0], end[1] - start[1]))
        return res

    update_wrapper(new_fcn, fcn)
    return new_fcn
