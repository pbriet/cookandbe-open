
from rest_framework             import viewsets
from rest_framework.decorators  import api_view, permission_classes
from rest_framework.response    import Response
from rest_framework.exceptions  import NotAuthenticated
from rest_framework.permissions import AllowAny

from django.db                  import transaction
from django.db.models           import Q, F, Max
from django.core.exceptions     import PermissionDenied
from django.utils               import timezone

from common.permissions         import Or, ReadOnly, ReadWrite
from common.decorators          import api_model_arg, api_arg
from common.rest                import LimitOffsetViewSetMixin, DefaultPagination

from discussion.models          import Discussion, Message, Publication
from discussion.controls        import send_new_message_email, send_new_question_email, send_new_response_email
from discussion.serializers     import DiscussionSerializer, MessageSerializer
from discussion.serializers     import PublicationSerializer, PartialPublicationSerializer

from user_mgr.models            import User

@api_view(['GET'])
@permission_classes((AllowAny,))
@api_arg('key', str)
def publication_from_key(request, key):
    try:
        publication = Publication.objects.get(url_key = key)
    except Publication.DoesNotExist:
        return Response({"exists": False}, 200)
    if request.user.is_authenticated: serializer = PublicationSerializer
    else:                             serializer = PartialPublicationSerializer
    res = serializer(publication).data
    res["exists"] = True
    return Response(res)

@api_view(['GET'])
@api_arg("keywords", str, "")
@api_arg("hidden", bool, False)
@permission_classes((AllowAny,))
def api_search_publications(request, keywords, hidden):
    if request.user.is_authenticated and (request.user.is_dietician or request.user.is_admin):
        queryset = Publication.objects.all()
        if hidden:
            queryset = queryset.filter(public = False)
    else:
        queryset = Publication.objects.filter(public = True)
    # Global settings
    queryset = queryset.prefetch_related('author')
    queryset = queryset.order_by('-creation_date')
    if keywords:
        for word in keywords.split(' '):
            queryset = queryset.filter(question__icontains = word)
    # Response
    count       = queryset.count()
    queryset    = DefaultPagination().paginate_queryset(queryset, request)
    if request.user.is_authenticated: serializer = PublicationSerializer
    else:                             serializer = PartialPublicationSerializer
    data        = serializer(queryset, many = True).data
    return Response({"results": data, "count" : count, "keywords" : keywords}, 200)

class PublicationViewSet(LimitOffsetViewSetMixin, viewsets.ModelViewSet):
    LIMIT_DEFAULT       = 10
    LIMIT_MAX           = 30
    model               = Publication
    permission_classes  = (Or(ReadWrite("admin", list = True), ReadWrite("dietician", list = True), ReadOnly(list = True)), )

    def get_serializer_class(self):
        if self.request.user.is_authenticated:
            return PublicationSerializer
        else:
            return PartialPublicationSerializer

    def get_queryset(self):
        if self.request.user.is_authenticated and (self.request.user.is_dietician or self.request.user.is_admin):
            queryset = Publication.objects.all()
        else:
            queryset = Publication.objects.filter(public = True)
        queryset = queryset.prefetch_related('author')
        queryset = queryset.order_by('-creation_date')
        return queryset

class DiscussionViewSet(LimitOffsetViewSetMixin, viewsets.ModelViewSet):
    LIMIT_DEFAULT       = 10
    LIMIT_MAX           = 30
    model               = Discussion
    serializer_class    = DiscussionSerializer
    permission_classes  = (Or(
        ReadWrite(user = ("dietician", ), list = True),
        ReadOnly("dietician", list = True),
        ReadWrite(user = ("owner", ), list = True),
        ReadOnly("admin", list = True),
    ),)

    def get_queryset(self):
        user = self.request.user
        if not user.is_authenticated:
            raise NotAuthenticated
        dietician_mode = user.is_dietician or user.is_admin
        return DiscussionViewSet._get_filtered_queryset(self.request, dietician_mode)

    @staticmethod
    def _get_filtered_queryset(request, dietician_mode):
        if dietician_mode:
            if not request.user.is_dietician and not request.user.is_admin:
                raise PermissionDenied
            queryset = Discussion.objects.all()
            queryset = queryset.prefetch_related('messages', 'messages__author', 'publication')
        else:
            queryset = Discussion.objects.filter(owner_id = request.user.id)
            queryset = queryset.prefetch_related('messages', 'messages__author')
        queryset = queryset.order_by('-last_date')
        return queryset

    @staticmethod
    @api_view(['POST'])
    @api_arg("close", bool)
    @api_model_arg("discussion", Discussion)
    def status(request, discussion, close):
        user = request.user
        if not user.is_authenticated or (not user.is_admin and not (user.is_dietician and discussion.dietician_id == user.id)):
            raise PermissionDenied
        if close:
            discussion.close_date = timezone.now()
        else:
            discussion.close_date = None
        discussion.save()
        return Response({ "close_date": discussion.close_date }, 200)

    @staticmethod
    @api_view(['POST'])
    @api_model_arg("user", User)
    @api_model_arg("discussion", Discussion)
    def read(request, user, discussion):
        if not user.is_authenticated or not user in (discussion.owner, discussion.dietician):
            raise PermissionDenied
        if request.user.id != user.id and not request.user.is_admin:
            raise PermissionDenied
        if user.id == discussion.owner_id:
            discussion.owner_read_date = timezone.now()
        else:
            discussion.dietician_read_date = timezone.now()
        discussion.save()
        return Response({ "owner_read_date": discussion.owner_read_date, "dietician_read_date": discussion.dietician_read_date }, 200)

    @staticmethod
    @api_view(['GET'])
    @api_arg("keywords", str, "")
    @api_arg("unread", bool, False)
    @api_arg("dietician_mode", bool, False)
    def search(request, keywords, unread, dietician_mode):
        queryset = DiscussionViewSet._get_filtered_queryset(request, dietician_mode)
        if keywords:
            for word in keywords.split(' '):
                queryset = queryset.filter(title__icontains = word)
        if unread:
            if dietician_mode:
                where = Q(dietician__isnull = True) | Q(last_date__gte = F("dietician_read_date"), dietician = request.user)
            else:
                where = Q(last_date__gte = F("owner_read_date"), owner = request.user)
            queryset = queryset.filter(where)
        # Response
        count       = queryset.count()
        queryset    = DefaultPagination().paginate_queryset(queryset, request)
        data        = DiscussionSerializer(queryset, many = True).data
        return Response({"results": data, "count" : count, "keywords" : keywords}, 200)

    @api_model_arg('owner', User, id_arg_name = "owner")
    @transaction.atomic
    def create(self, request, owner, *args, **kargs):
        if owner.id != request.user.id:
            raise PermissionDenied
        quota = owner.question_quota
        if quota.question_count >= quota.max_questions:
            raise PermissionDenied
        response = super(DiscussionViewSet, self).create(request, *args, **kargs)
        if response.status_code == 201:
            send_new_question_email(Discussion.objects.get(pk = response.data['id']))
        return response

    def update(self, request, *args, **kargs):
        if not request.user.is_authenticated or not request.user.is_admin:
            raise PermissionDenied
        response = super().update(request, *args, **kargs)
        return response

    @staticmethod
    @api_view(['POST'])
    @api_model_arg("discussion", Discussion)
    @api_model_arg("publication", Publication)
    def set_publication(request, discussion, publication):
        if not request.user.is_authenticated or not True in (request.user.is_admin, request.user.is_dietician):
            raise PermissionDenied
        if not request.user.is_admin and publication.author_id != request.user.id:
            raise PermissionDenied
        discussion.publication_id = publication.id
        discussion.save()
        return Response(DiscussionSerializer(discussion).data, 200)

    def destroy(self, request, *args, **kargs):
        if not request.user.is_authenticated or not request.user.is_admin:
            raise PermissionDenied
        super().destroy(self, request, *args, **kargs)

class MessageViewSet(viewsets.ModelViewSet):
    queryset = Message.objects.all()
    serializer_class = MessageSerializer
    permission_classes = (Or(
        ReadOnly("dietician"),
        ReadWrite(user = ("author", )),
        ReadWrite(user = ("discussion", "dietician")),
        ReadWrite(user = ("discussion", "owner")),
        ReadWrite("admin"),
    ), )

    @api_model_arg('discussion', Discussion, id_arg_name = "discussion")
    @api_model_arg('author', User, id_arg_name = "author")
    @transaction.atomic
    def create(self, request, discussion, author, *args, **kargs):
        if discussion.close_date is not None or request.user.id != author.id:
            # Discussion closed or being hacked
            raise PermissionDenied
        if author not in (discussion.dietician, discussion.owner):
            if discussion.dietician is None and author.is_dietician:
                discussion.dietician = author
                discussion.save()
            else:
                raise PermissionDenied
        response = super(MessageViewSet, self).create(request, *args, **kargs)
        if author.id == discussion.owner_id and discussion.dietician is not None and discussion.nb_unread_messages(discussion.dietician_id) == 1:
            send_new_message_email(discussion)
        elif author.id == discussion.dietician_id and discussion.nb_unread_messages(discussion.owner_id) == 1:
            send_new_response_email(discussion)
        return response

    def destroy(self, request, pk = None):
        if not request.user.is_authenticated or not request.user.is_admin:
            raise PermissionDenied
        return super().destroy(self, request, pk)
