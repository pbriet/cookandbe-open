#!/usr/bin/env python
from bases.op_base      import DjangoMuninScript
from user_mgr.models    import User

class NbUsers(DjangoMuninScript):
    def apply_config(self):
        print("graph_title Number of users in the database")
        print('graph_category users')
        print('graph_args --lower-limit 0')
        print("disabled.draw AREA")
        print("disabled.label # unsubscribed")
        print("disabled.colour 777777")
        print("enabled.draw STACK")
        print("enabled.label # cookandbe")
        print("enabled.colour 00FF00")
        print("biodymanager.draw STACK")
        print("biodymanager.label # biodymanager")
        print("biodymanager.colour 00AA00")


    def apply_values(self):
        nb_disabled = User.objects.filter(enabled=False).count()
        print("disabled.value %i" % nb_disabled)
        nb_active = User.objects.filter(enabled=True, biodymanager_id__isnull=True).count()
        print("enabled.value %i" % nb_active)
        biodymanager = User.objects.filter(enabled=True, biodymanager_id__isnull=False).count()
        print("biodymanager.value %i" % biodymanager)


NbUsers().apply()