
from rest_framework             import viewsets
from rest_framework.response    import Response
from common.permissions         import IsOwner
from eater_mgr.models           import Eater
from eater_mgr.serializers      import EaterSerializer

class UserEaterViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = EaterSerializer
    permission_classes = (IsOwner('user', list = True), )

    def get_queryset(self):
        user_id = int(self.kwargs['user_id'])
        return Eater.objects.filter(user_id = user_id)