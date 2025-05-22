from common.rest                import TreeLikeViewSetMixin
from rest_framework             import viewsets
from location_mgr.serializers   import LocationSerializer
from location_mgr.models        import Location

class LocationViewSet(TreeLikeViewSetMixin, viewsets.ModelViewSet):
    queryset = Location.objects.all()
    serializer_class = LocationSerializer
