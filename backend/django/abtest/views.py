from abtest.controller          import ab_value, ab_success
from abtest.models              import AbCampaign

from collections                import defaultdict

from rest_framework             import viewsets, serializers
from rest_framework.decorators  import permission_classes, api_view
from rest_framework.permissions import AllowAny
from rest_framework.response    import Response

from common.decorators          import api_arg, api_model_arg, api_cookie_arg
from common.permissions         import Allow, ReadOnly


class AbCampaignSerializer(serializers.ModelSerializer):
    class Meta:
        model = AbCampaign
        exclude = []

class AbCampaignViewSet(viewsets.ModelViewSet):
    queryset = AbCampaign.objects.all()
    permission_classes = (ReadOnly("admin", list = True),)
    serializer_class = AbCampaignSerializer

@api_view(['GET'])
@permission_classes((Allow('admin'),))
@api_model_arg('campaign', AbCampaign, id_arg_name="campaign_key", pk_name="key", pk_type=str)
def ab_campaign_results(self, campaign):
    """
    Return the campaign results :
    for each objective, what is the % of success / cumulative value
    depending on option
    """
    options = campaign.options.all()
    option_id_to_key = dict((option.id, option.key) for option in options)

    choices = campaign.choices.prefetch_related('records').all()

    # Number of options tested, per option key
    count_options = defaultdict(int)
    # For each objective, For each option, how many are reached - cumulative  (multiple reached objective)
    cumulative_values = defaultdict(lambda: defaultdict(float))
    # For each objective, For each option, how many are reached (max. 1 per user - to get a percentage of success)
    unique_values = defaultdict(lambda: defaultdict(float))

    all_objectives = set()

    for choice in choices:
        # This user had this option enabled.
        option_key = option_id_to_key[choice.option_id]
        count_options[option_key] += 1

        # For this user, how many success for each objective
        objectives_reached = defaultdict(int)
        for record in choice.records.all():
            objectives_reached[record.objective] += 1

        for objective, nb_success in objectives_reached.items():
            cumulative_values[objective][option_key] += nb_success # Cumulative
            unique_values[objective][option_key] += 1  # Unique

            all_objectives.add(objective)

    # Normalization
    for objective in all_objectives:
        for option_key, nb in count_options.items():
            cumulative_values[objective][option_key] = round(cumulative_values[objective][option_key] / nb, 2)
            unique_values[objective][option_key] = round(unique_values[objective][option_key] * 100. / nb, 2)

        cumulative_values[objective] = dict(cumulative_values[objective])
        unique_values[objective] = dict(unique_values[objective])

    return Response({"key": campaign.key, "description": campaign.description,
                     "percentage": dict(unique_values), "avg_value": dict(cumulative_values)})


@api_view(['GET'])
@permission_classes((AllowAny, ))
@api_cookie_arg('op_uuid', error_code=200)
@api_model_arg('campaign', AbCampaign, id_arg_name="campaign_key", pk_name="key", pk_type=str)
def api_ab_value(request, op_uuid, campaign):
    """
    For this visitor, returns the option selected for this campaign
    """
    return Response({"key": ab_value(request.user, op_uuid, campaign=campaign)})

@api_view(['POST'])
@permission_classes((AllowAny, ))
@api_cookie_arg('op_uuid', error_code=200)
@api_model_arg('campaign', AbCampaign, id_arg_name="campaign_key", pk_name="key", pk_type=str)
@api_arg('objective', str)
def api_ab_success(request, op_uuid, campaign, objective):

    if not ab_success(request.user, op_uuid, objective, campaign=campaign) :
        # Not returning a 400 --  not worth an error message client-side !
        return Response({"status": "error", "error": "abchoice is not initialized"})

    return Response({"status": "ok"})