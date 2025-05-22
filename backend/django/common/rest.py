"""
Provides helpers for serialization and REST communication
"""

from rest_framework.response    import Response
from rest_framework             import viewsets, serializers
from rest_framework.routers     import Route, SimpleRouter
from rest_framework.fields      import FloatField, ImageField
from rest_framework.pagination  import LimitOffsetPagination
from optalim.settings           import MEDIA_ROOT
from django.db.models.query     import QuerySet

import json
import copy

class MinValueValidator(object):
    def __init__(self, value):
        self.value = value
    def __call__(self, x):
        if x < self.value:
            raise serializers.ValidationError("Value is too low")

class MaxValueValidator(object):
    def __init__(self, value):
        self.value = value
    def __call__(self, x):
        if x > self.value:
            raise serializers.ValidationError("Value is too high")

class FlexibleFloatField(FloatField):
    """
    Float field that converts commas into dots, so that both are allowed as
    decimal separator
    """
    def from_native(self, value):
        if type(value) is str:
            value = value.replace(",", ".")
        return super().from_native(value)

class CustomViewSet(viewsets.ModelViewSet):
    """
    Class allowing advanced request control through URL parameters.

    To apply a filter from the view:
    1. Server: set the class attribute filtered_fields in the inheritant class. Example: filtered_fields = ('tag_id', 'food_id').
    2. View: add the wanted filtering value as parameter in the URL. Example: .../api/food_tag_set?tag_id=1&food_id=139
    """
    def get_queryset(self):
        assert hasattr(self, "model"), "Model is missing"
        queryset = self.model.objects.all()
        # Checking filters
        if hasattr(self, "filtered_fields"):
            filterDict = dict()
            for fieldName in self.filtered_fields:
                filterValue = self.request.query_params.get(fieldName, None)
                if filterValue is None:
                    continue
                filterDict[fieldName] = filterValue
            queryset = queryset.filter(**filterDict)
        return queryset

class TreeLikeViewSetMixin(object):
    """
    When a resource is tree-like  (the model has a "parent" attribute of
                                   same type)
    Tweak the GET and add the option "tree=1" that returns a JSON object
    reflecting the hierarchy, instead of a flat list.

    without tree == 1:
    [{"id": 1, "name": "dad", "parent": None}, {"id": 2, "name": "child", "parent": 1}]

    with tree == 1:
    [{"id": 1, "name" : "dad", "children": [{"id": 2, "name": "child", "children": []}]}]
    """
    PARENT_ATTRIBUTE_NAME = "parent"

    def list(self, request, *args, **kwargs):
        response = super(TreeLikeViewSetMixin, self).list(request, *args, **kwargs)
        if 'tree' in self.request.query_params and self.request.query_params['tree'] :
            # Refactoring the objects in a tree-like structure
            res_data = []
            obj_per_id = {}
            for serialized_obj in response.data:
                serialized_obj['children'] = []
                obj_per_id[serialized_obj['id']] = serialized_obj

            for obj_id in list(obj_per_id.keys()):
                obj = obj_per_id[obj_id]
                parent_id = obj_per_id[obj_id].pop(self.PARENT_ATTRIBUTE_NAME)
                if parent_id:
                    obj_per_id[parent_id]['children'].append(obj)
                else:
                    # Keep "root" objects in a separate list that will be returned
                    res_data.append(obj)

            nb_nodes = self.__count_nodes(res_data)
            if nb_nodes < len(response.data):
                assert False, "probable recursive tree"

            response.data = res_data
        return response

    def __count_nodes(self, tree_data):
        """
        Returns the number of nodes in the tree
        """
        res = 0
        for tree_elt in tree_data:
            res += 1 + self.__count_nodes(tree_elt['children'])
        return res

class DefaultPagination(LimitOffsetPagination):
    default_limit = 10
    max_limit     = 50

class LimitOffsetViewSetMixin(object):
    pagination_class = LimitOffsetPagination

class AddRemoveManyToManyViewSetMixin(object):
    """
    Mixin that provides helpers to add/remove many to many attributes
    """
    def _add_many_object(self, request, other_obj_collection, field_name, id_key, reverse_key=None):
        """
        Add one more ManyToMany relation
        @param other_obj_collection: model of the other ManyToMany resource
        @param field_name: ManyToManyField
        @param id_key: string key in body request that contains the object id
        @param reverse_key: if this is a ManyToManyField _through_ an other table, we need the name
                            of the attribute that refers to this resource
        """
        params = json.loads(request.body.decode("utf-8"))
        other_obj = object_from_params_id(other_obj_collection, params, id_key)
        if isinstance(other_obj, Response):
            return other_obj  # Failure

        obj = self.get_object()
        many_to_many_field = getattr(obj, field_name)

        if other_obj.id in [m.id for m in many_to_many_field.all()]:
            # Avoid duplication
            return Response(status=200)

        if reverse_key is None:
            # If there is no "through", it works as simply as that
            many_to_many_field.add(other_obj)
        else:
            # But with a "through", it gets more complicated
            kargs = {id_key: other_obj.id, reverse_key: obj.id}
            many_to_many_field.through.objects.create(**kargs)

        return Response(status=200)

    def _remove_many_object(self, request, other_obj_collection, field_name, id_key, reverse_key=None):
        """
        Remove one ManyToMany relation
        @param reverse_key: if this is a ManyToManyField _through_ an other table, we need the name
                            of the attribute that refers to this resource
        """
        params = json.loads(request.body.decode("utf-8"))
        other_obj = object_from_params_id(other_obj_collection, params, id_key)
        if isinstance(other_obj, Response):
            return other_obj  # Failure

        obj = self.get_object()
        many_to_many_field = getattr(obj, field_name)
        if reverse_key is None:
            # If there is no "through", it works as simply as that
            many_to_many_field.remove(other_obj)
        else:
            # But with a "through", it gets more complicated
            kargs = {id_key: other_obj.id, reverse_key: obj.id}
            through_relation = many_to_many_field.through.objects.get(**kargs)
            through_relation.delete()

        return Response(status=200)

def object_from_params_id(collection, params, key):
    """
    Returns an object from :
    * a collection
    * some parameters (dictionnary)
    * a key in this dictionnary

    check that the key is correctly defined, is an id,
    and that the object exists
    """
    if key not in params:
        return Response({"error": "%s not set" % key}, 400)

    try:
        id_value = int(params[key])
    except ValueError:
        return Response({"error": "%s is not an id" % key}, 400)

    if not collection.objects.filter(pk=id_value).exists():
        return Response({"error": "id %s doesn't exist" % id_value}, 400)

    return collection.objects.get(pk=id_value)

class ReadOnlyRouter(SimpleRouter):
    """
    A router for read-only APIs, which doesn't use trailing slashes.
    """
    def get_routes(self, viewset):
        res = copy.copy(super().get_routes(viewset))

        ro_routes = []
        for route in res:
            mapping_copy = copy.copy(route.mapping)
            for method in ('post', 'put', 'patch'):
                if method in mapping_copy:
                    mapping_copy.pop(method)
            ro_route = Route(url=route.url,
                             mapping=mapping_copy,
                             name=route.name,
                             initkwargs=route.initkwargs,
                             detail=True)
            if len(ro_route.mapping):
                ro_routes.append(ro_route)
        return ro_routes

class SerializerWithCustomFields(serializers.ModelSerializer):
    """
    Serializer that overrides the data property, and call a fill_additional_data method
    """

    def to_representation(self, instance):
        """
        Serialize the object : parent method + retrieval of ingredient names + conversions
        """
        results = super().to_representation(instance)
        if isinstance(instance, list):
            for index, obj in enumerate(instance):
                self.fill_additional_data(obj, results[index])
        elif instance is not None:
            self.fill_additional_data(instance, results)
        return results

    def has_many_objs(self):
        """
        Returns True if we are currently serializing a list of objects
        """
        return len(self._args) > 0 and type(self._args[0]) in (tuple, list, QuerySet)

    def fill_additional_data(self, obj, result):
        pass

