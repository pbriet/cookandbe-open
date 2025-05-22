from django.contrib     import admin
from user_mgr.models    import User, ProUser, ConfigStage

admin.site.register(User)
admin.site.register(ProUser)
admin.site.register(ConfigStage)