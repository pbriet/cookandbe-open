
from paybox.models          import Subscription
from common.rest            import SerializerWithCustomFields

class SubscriptionSerializer(SerializerWithCustomFields):
    class Meta:
        model = Subscription
        exclude = []

    def fill_additional_data(self, subscription, result):
        result['transactions'] = subscription.get_transaction_refs()
