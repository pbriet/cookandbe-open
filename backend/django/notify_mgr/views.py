from rest_framework.decorators      import action
from rest_framework.response        import Response
from profile_mgr.models             import Profile
from notify_mgr.models              import Information
from notify_mgr.serializers         import InformationSerializer
from django.utils                   import timezone
from django.core.exceptions         import PermissionDenied
from rest_framework                 import generics, viewsets
import datetime


class NotificationsViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = InformationSerializer

    def get_queryset(self):
        user_id = int(self.kwargs['user_id'])
        return Information.objects.exclude(readers__id=user_id).\
                                        exclude(valid_until__lt=timezone.now()).\
                                        order_by('creation_date')

    def list(self, request, *args, **kwargs):
        """
        Returns a list of notifications for a given user
        """
        user_id = int(self.kwargs['user_id'])
        if user_id != self.request.user.id:
            raise PermissionDenied
        objs = list(self.get_queryset())

        if Profile.objects.filter(creator_id=user_id).count() == 1:
            profile = Profile.objects.get(creator_id=user_id)
            if profile.weight is None or profile.height is None:
                objs.insert(0, Information(can_be_read=False,
                                        title="Poids/Taille non définis",
                                        content="Afin d'obtenir des plannings vraiment sur mesure, " +\
                                                "veuillez renseigner votre poids et taille",
                                        action="profile",
                                        priority=5,
                                        label="conf"))

            if profile.tastes.count() == 0 and profile.restrictions.count() == 0:
                objs.insert(0, Information(can_be_read=False,
                                        title="Goûts non définis",
                                        content="Vous n'avez pas défini les aliments que vous n'aimez pas",
                                        action="tastes",
                                        priority=4,
                                        label="conf"))

        return Response(InformationSerializer(objs, many = True).data, 200)

    @action(detail=True, methods=['post'])
    def read(self, request, pk, user_id):
        user_id = int(self.kwargs['user_id'])
        if user_id != self.request.user.id:
            raise PermissionDenied
        info = Information.objects.get(pk=pk)
        info.readers.add(self.request.user)
        info.save()
        return Response({"status": "done"}, status=201)
