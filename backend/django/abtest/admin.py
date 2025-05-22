from django.contrib     import admin
from abtest.models      import AbCampaign, AbOption

admin.site.register(AbCampaign)
admin.site.register(AbOption)