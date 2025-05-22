from common.rest            import SerializerWithCustomFields
from common.model           import AutoUrlKeyModel

from diet_mgr.models        import Diet

from paybox.prices          import get_prices_and_discount

class DietSerializer(SerializerWithCustomFields):
    class Meta:
        model = Diet
        fields = ('key', 'title', 'enabled', 'description', 'id', 'default_display',
                  'min_subscription_level', 'has_diagnostic', 'free_trial_days', 'url_key')

    def is_valid(self, *args, **kargs):
        self.initial_data = dict(self.initial_data.items())
        if "title" in self.initial_data and "url_key" not in self.initial_data:
            self.initial_data['url_key'] = AutoUrlKeyModel._build_base_key(self.initial_data["title"])
        return super().is_valid(*args, **kargs)

    def fill_additional_data(self, diet, result):
        if diet.get_min_subscription_level() == 0:
            return
        level_prices = get_prices_and_discount()[diet.get_min_subscription_level()]
        for nb_months, tariff in level_prices.items():
            result['cost_%i' % nb_months] = float(tariff['after_discount']) / 100
