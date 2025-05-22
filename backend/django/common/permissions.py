
from rest_framework.permissions     import BasePermission, SAFE_METHODS
from rest_framework                 import viewsets
from user_mgr.models                import Role, User, ProUser

class RolePermission(BasePermission):

    ROLE = None
    ROLE_NAME = None
    USER = None
    LIST = False
    READ = False
    WRITE = False
    VIEWSET = False

    def __init__(self, *args, **kargs):
        super().__init__(*args, **kargs)
        if isinstance(self.USER, str): self.USER = (self.USER, )
        assert self.USER is not True
        if self.ROLE is None and self.ROLE_NAME is not None:
            self.ROLE = Role.objects.get(name = self.ROLE_NAME)

    def has_permission(self, request, view):
        assert self.VIEWSET is self.is_viewset(view), "Permission not allowed. " \
            + ("User Allow for standalone methods", "Use Read/Write for ViewSets %s" % view.__class__.__name__)[self.VIEWSET]
        if self.ROLE is not None and not self.is_user_allowed(request.user, self.ROLE):
            return False
        if self.READ is False and request.method in SAFE_METHODS:
            return False
        if self.WRITE is False and request.method not in SAFE_METHODS:
            return False
        if self.LIST is False and self.is_list_query(request):
            return False
        if self.USER is not None and request.user.is_anonymous:
            return False
        return True

    def is_viewset(self, view):
        return isinstance(view, viewsets.ModelViewSet) or isinstance(view, viewsets.ReadOnlyModelViewSet)

    def has_object_permission(self, request, view, obj):
        if self.USER is not None and self.get_recursive_attr(obj) != request.user:
            return False
        return True

    def get_recursive_attr(self, obj):
        for field_name in self.USER:
            obj = getattr(obj, field_name)
        return obj

    def is_user_allowed(self, user, role):
        return isinstance(user, User) and user.user_roles.filter(role_id = role.id).count() > 0

    def is_list_query(self, request):
        return request.method in SAFE_METHODS and request.parser_context["kwargs"].get("pk", None) is None

class PermissionOperation(BasePermission):
    PERMISSION_CLASSES = tuple()

    def __init__(self, *args, **kargs):
        self.permissions = list()
        for permission_class in self.PERMISSION_CLASSES:
            self.permissions.append(permission_class(*args, **kargs))

class OrPermission(PermissionOperation):
    def has_permission(self, request, view):
        for permission in self.permissions:
            allowed = permission.has_permission(request, view)
            if allowed:
                return True
        return False

    def has_object_permission(self, request, view, obj):
        for permission in self.permissions:
            allowed = permission.has_object_permission(request, view, obj)
            """
            Attention:
            ==========
            Techniquement l'appel à has_permission() peut déjà avoir eu lieu. Cependant, comme on est
            dans un Or, il suffit qu'une des permissions soit passée pour que l'on valide la première
            étape. Donc rien ne garantit que c'est cette même permission qui l'a passée. C'est pourquoi
            il faut revérifier que cette permission passe bien la première étape.
            """
            if allowed and permission.has_permission(request, view):
                return True
        return False

class AndPermission(PermissionOperation):
    def has_permission(self, request, view):
        for permission in self.PERMISSIONS:
            allowed = permission.has_permission(request, view)
            if not allowed:
                return False
        return True

    def has_object_permission(self, request, view, obj):
        for permission in self.PERMISSIONS:
            allowed = permission.has_object_permission(request, view, obj)
            if not allowed:
                return False
        return True

##### Some shortcuts #####

def Allow(role_name = None, user = None):
    class cls(RolePermission):
        ROLE_NAME = role_name
        USER = user
        LIST = True # Mandatory to avoid the 'missing pk' message
        READ = True
        WRITE = True
        VIEWSET = False
    return cls

def ReadWrite(role_name = None, user = None, list = False):
    class cls(RolePermission):
        ROLE_NAME = role_name
        USER = user
        LIST = list
        READ = True
        WRITE = True
        VIEWSET = True
    return cls

def ReadOnly(role_name = None, user = None, list = False):
    class cls(RolePermission):
        ROLE_NAME = role_name
        USER = user
        LIST = list
        READ = True
        WRITE = False
        VIEWSET = True
    return cls

def WriteOnly(role_name = None, user = None):
    class cls(RolePermission):
        ROLE_NAME = role_name
        USER = user
        LIST = False
        READ = False
        WRITE = True
        VIEWSET = True
    return cls

def And(*args):
    class cls(AndPermission):
        PERMISSION_CLASSES = args
    return cls

def Or(*args):
    class cls(OrPermission):
        PERMISSION_CLASSES = args
    return cls

IsAdmin                 = ReadWrite("admin", list = True)
IsAdminOrReadOnly       = Or(IsAdmin, ReadOnly())
IsAdminOrReadOnlyList   = Or(IsAdmin, ReadOnly(list = True))

def IsOwner(*field_names, list = False):
    return ReadWrite(user = field_names, list = list)

def IsOwnerOrReadOnly(*field_names, list = True):
    return Or(ReadWrite(user = field_names, list = list), ReadOnly())

def IsAdminOrOwnerElseReadOnly(*field_names, list = False):
    return Or(IsAdmin, ReadWrite(user = field_names, list = list), ReadOnly())

class IsStaff(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_staff

class IsPro(BasePermission):
    def has_permission(self, request, view):
        return isinstance(request.user, ProUser)
