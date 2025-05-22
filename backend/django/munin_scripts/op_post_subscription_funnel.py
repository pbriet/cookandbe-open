#!/usr/bin/env python
from bases.op_base      import DjangoMuninScript
from user_mgr.models    import User, ConfigStage

class PostSubscriptionFunnel(DjangoMuninScript):
    def apply_config(self):
        print("graph_title Post-subscription funnel (last 2 weeks)") # Last 2 weeks, except last 2 days (give time to users !)
        print('graph_category users')
        print('graph_args --lower-limit 0')
        print("avg_completion.draw LINE1")
        print("avg_completion.label average % completion")
        print("full_completion.draw LINE1")
        print("full_completion.label % with full completion")
        print("empty_completion.draw LINE1")
        print("empty_completion.label % with at most one completion")
        print("day_planner_visited.draw LINE1")
        print("day_planner_visited.label % having visited day_planner")
        print("shopping_list.draw LINE1")
        print("shopping_list.label % having created a shopping list")

    def apply_values(self):
        nb_stages = ConfigStage.objects.count()

        nb_completion = 0
        nb_users = 0
        nb_day_planner_visits = 0
        nb_shopping_list = 0
        nb_empty_completion = 0
        nb_full_completion = 0

        users = User.objects.filter(date_joined__gte=self.TWO_WEEKS_AGO,
                                    date_joined__lte=self.TWO_DAYS_AGO).prefetch_related("config_stage_completions",
                                                                                         "days",
                                                                                         "shopping_lists")
        for user in users:
            nb_users += 1
            nb_user_completion = user.config_stage_completions.count()
            if nb_user_completion <= 1:
                nb_empty_completion += 1
            elif nb_user_completion == nb_stages:
                nb_full_completion += 1
            nb_completion += nb_user_completion
            for day in user.days.all():
                if day.is_validated():
                    nb_day_planner_visits += 1 # At least one day validated (click on add to shopping list)
                    break
            if len(user.shopping_lists.all()) > 0:
                nb_shopping_list += 1

        if nb_users * nb_stages == 0:
            return

        avg_completion          = 100 * float(nb_completion) / (nb_users * nb_stages)
        avg_day_planner_visits  = 100 * float(nb_day_planner_visits) / nb_users
        avg_shopping_list       = 100 * float(nb_shopping_list) / nb_users
        avg_empty_completion    = 100 * float(nb_empty_completion) / nb_users
        avg_full_completion     = 100 * float(nb_full_completion) / nb_users

        print("avg_completion.value %.2f" % avg_completion)
        print("day_planner_visited.value %.2f" % avg_day_planner_visits)
        print("shopping_list.value %.2f" % avg_shopping_list)
        print("full_completion.value %.2f" % avg_full_completion)
        print("empty_completion.value %.2f" % avg_empty_completion)


PostSubscriptionFunnel().apply()