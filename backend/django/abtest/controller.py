from abtest.models              import AbCampaign, AbChoice, AbRecord

import random

def init_ab_choice(campaign, user, unique_id):
    """
    Randomly select an option and create a choice associated to the user/unique_id
    """
    if user.is_anonymous:
        user = None

    options = list(campaign.options.all())
    option = random.choice(options)

    return AbChoice.objects.create(campaign=campaign, user=user, unique_id=unique_id,
                                   option=option)

def find_ab_choice(campaign, user, unique_id):
    """
    Find the ab choice corresponding to the user/unique_id
    """
    choices = []
    if not user.is_anonymous:
        # Is there any choice associated to the user ?
        choices = list(campaign.choices.filter(user=user))
    if len(choices) == 0:
        # Any choice associated to the unique_id ?
        choices = list(campaign.choices.filter(unique_id=unique_id))
    if len(choices) == 0:
        return None
    return choices[0]


def ab_value(user, unique_id, campaign=None, campaign_key=None):
    """
    For this visitor, returns the option selected for this campaign
    """
    if campaign is None:
        assert campaign_key is not None
        campaign = AbCampaign.object.get(key=campaign_key)

    choice = find_ab_choice(campaign, user, unique_id)
    if choice is None:
        # Right, no option has been created yet.
        # Initialization
        choice = init_ab_choice(campaign, user, unique_id)

    # User is logged in but not associated to this choice
    if not user.is_anonymous and choice.user_id is None:
        choice.user = user
        choice.save()

    return choice.option.key

def ab_success(user, unique_id, objective, campaign=None, campaign_key=None):
    """
    Register an objective success related to a A/B campaign.
    """
    if unique_id is None:
        return False
    if campaign is None:
        assert campaign_key is not None
        campaign = AbCampaign.objects.get(key=campaign_key)

    choice = find_ab_choice(campaign, user, unique_id)
    if choice is None:
        return False

    AbRecord.objects.create(choice=choice, objective=objective)
    return True