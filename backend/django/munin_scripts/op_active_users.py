#!/usr/bin/env python
from op_base            import DjangoMuninScript
from user_mgr.models    import User

class ActiveUsers(DjangoMuninScript):
    def apply_config(self):
        print("graph_title Users that joined more than 2 weeks ago and were active in the last 10 days")
        print('graph_category users')
        print("nb_users.draw LINE1")
        print("nb_users.label # users")
    
    def apply_values(self):
        
        # Users that joined before date, and were active during this period
        nb_users = User.objects.filter(days__creation_date__gte=self.TEN_DAYS_AGO,
                                       days__skipped=False,
                                       user_roles=None,
                                       date_joined__lt=self.TWO_WEEKS_AGO).distinct().count()
        print("nb_users.value %i" % nb_users)


ActiveUsers().apply()