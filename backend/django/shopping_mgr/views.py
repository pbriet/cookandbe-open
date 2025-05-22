
from django.db                  import transaction
from django.core.exceptions     import PermissionDenied
from django.http                import Http404

from rest_framework             import viewsets
from rest_framework.decorators  import api_view
from rest_framework.response    import Response

from common.date                import today
from common.decorators          import api_check_user_id, api_model_arg, api_arg
from common.permissions         import Or, ReadOnly, ReadWrite, IsAdminOrReadOnly

from emailing                   import SendmailError
from emailing.tools             import sendmail_template, MessageType

from planning_mgr.controller.planning   import days_shopping_listable
from planning_mgr.models        import Day

from shopping_mgr.controller    import fill_shopping_list
from shopping_mgr.models        import ShoppingList, ShoppingItem, ShoppingCategory
from shopping_mgr.serializers   import ShoppingListSerializer, ShoppingItemSerializer, ShoppingListExtendedSerializer, ShoppingCategorySerializer

import datetime

def shopping_list_decorator(raise404=False):
    def decorator(fcn):
        """
        Decorator that retrieves a shopping list from its id, and checks that it belongs to the user
        """
        @api_arg('shopping_list_id', int)
        def new_fcn(request, shopping_list_id, **kargs):
            try:
                shopping_list = ShoppingList.objects.get(pk=shopping_list_id)
            except:
                raise Http404("No such shoppint list")
            if shopping_list.user_id != request.user.id:
                return Response({"error": "shopping list doesn't belong to the user"}, 400)
            return fcn(request, shopping_list=shopping_list, **kargs)
        return new_fcn
    return decorator

def shopping_item_decorator(fcn):
    """
    Decorator that retrieves a shopping list from its id, and checks that it belongs to the user
    """
    @api_model_arg('shopping_item', ShoppingItem)
    def new_fcn(request, shopping_item, **kargs):
        if shopping_item.shopping_list.user_id != request.user.id:
            return Response({"error": "shopping item doesn't belong to the user"}, 400)
        return fcn(request, shopping_item=shopping_item, **kargs)
    return new_fcn

@api_view(['POST'])
@api_check_user_id
@api_arg('start_date', datetime.date)
@api_arg('end_date', datetime.date)
@transaction.atomic
def new_shopping_list(request, user_id, start_date, end_date):
    """
    Build a new shopping list
    """
    if request.user.days.filter(date__gte=start_date, date__lte=end_date, shopping_list__isnull=False).count() > 0:
        return Response({"status": "failed", "error": "contains_days_in_shopping_list"})
    shopping_list = ShoppingList.objects.create(user_id=user_id, start_date=start_date,
                                                end_date=end_date)
    fill_shopping_list(shopping_list)
    return Response({"status": "created", "shopping_list_id": shopping_list.id})

@api_view(['POST'])
@api_check_user_id
@shopping_list_decorator()
def delete_shopping_list(request, user_id, shopping_list):
    shopping_list.delete()
    return Response({"status": "done"}, 200)

@api_view(['GET'])
@api_check_user_id
@shopping_list_decorator(raise404=True)
def shopping_list_content(request, user_id, shopping_list):
    """
    Returns the content of a shopping list : foods and quantities, per category
    """
    value = ShoppingListExtendedSerializer(shopping_list).data
    return Response({"content": value,
                     "start_date": shopping_list.start_date,
                     "end_date": shopping_list.end_date})


@api_view(['GET'])
@api_check_user_id
@shopping_list_decorator(raise404=True)
def shopping_list_fly_menu(request, user_id, shopping_list):
    """
    Returns the content of the shopping list, formatted for Fly Menu
    """
    res = ShoppingListExtendedSerializer(shopping_list).get_fly_menu_data()
    return Response(res)


@api_view(['POST'])
@api_check_user_id
@shopping_list_decorator()
def send_list_by_email(request, user_id, shopping_list):
    """
    Send the content of a shopping list to the user email address
    """
    content = ShoppingListExtendedSerializer(shopping_list).data
    template_vars  = { "content" : content,
                       "start_date":shopping_list.start_date,
                       "end_date": shopping_list.end_date }
    try:
        sendmail_template(MessageType.REALTIME, 'shopping_mgr/templates/list_by_email.html', template_vars,
                          "Votre liste de courses", users = [request.user], send_async=False,
                          tags=['shopping_list'])
    except SendmailError as e:
        return Response({"status": "error", "title": "Échec de l'envoi du message, réessayez dans quelques minutes !", "details": e.details})
    return Response({"status": "ok"})


@api_view(['POST'])
@api_check_user_id
@shopping_item_decorator
def shopping_list_toggle_item(request, user_id, shopping_item):
    """
    Check / uncheck a food in a shopping list
    """
    shopping_item.got_it = not shopping_item.got_it
    shopping_item.save()
    return Response({"status": "ok"})


@api_view(['GET'])
@api_arg('limit', int, 5)
@api_check_user_id
def shopping_list_history(request, user_id, limit):
    """
    Returns the user history of shopping lists
    """
    lists = ShoppingList.objects.filter(user__id=user_id).order_by('-start_date')

    res = []

    for l in lists[:5]:
        res.append(ShoppingListSerializer(l).data)
    return Response({'lists': res}, 200)

@api_view(['GET'])
@api_check_user_id
def shopping_list_available_days(request, user_id):
    """
    Return the default dates for a new shopping_list :
    start_date : the first Day planned which is not already in a shopping_list
    end_date : the last Day planned
    planned_dates : all days available
    """
    planned_dates = [d.date for d in days_shopping_listable(user_id).only('date')]

    if len(planned_dates) == 0:
        return Response({'status': 'no_planned_day', 'planned_dates': planned_dates})
    return Response({'status': 'ok', 'start_date': min(planned_dates), 'end_date': max(planned_dates), 'planned_dates': planned_dates})

class ShoppingCategoryViewSet(viewsets.ModelViewSet):
    queryset = ShoppingCategory.objects.all()
    serializer_class = ShoppingCategorySerializer
    permission_classes = (IsAdminOrReadOnly, )

class ShoppingItemViewSet(viewsets.ModelViewSet):
    queryset = ShoppingItem.objects.all()
    serializer_class = ShoppingItemSerializer

    permission_classes = (Or(
        ReadWrite("admin"),
        ReadWrite(user = ("shopping_list", "user")),
    ), )

    def create(self, request, *args, **kwargs):
        shopping_list = ShoppingList.objects.get(pk = request.data['shopping_list'])
        if not request.user.is_admin and request.user.id != shopping_list.user_id:
            raise PermissionDenied
        for mandatory_arg in ('forced_name', 'forced_quantity'):
            if mandatory_arg not in request.data or not request.data[mandatory_arg]:
                raise PermissionDenied
        return super().create(request, *args, **kwargs)

    @staticmethod
    @api_view(['PUT'])
    @api_arg("quantity", str, None)
    @api_arg("name", str, None)
    @api_model_arg("item", ShoppingItem)
    def force(request, item, quantity, name):
        user = request.user
        if not user.is_authenticated or (not user.is_admin and item.shopping_list.user_id != user.id):
            raise PermissionDenied
        if item.food is None and None in (name, quantity):
            # Custom items must have quantity and name
            raise PermissionDenied
        item.forced_name = name
        item.forced_quantity = quantity
        item.save()
        return Response({ "status": "ok" }, 200)
