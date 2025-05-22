import yaml
from yaml.loader import FullLoader
import os
from optalim.settings import TESTING

FILE_PATH = os.path.abspath(os.path.dirname(__file__))

# Config is just a namespace
class Config(object):

    @classmethod
    def load_anc(cls):
        if TESTING :
            cls.anc = {}
            return
        with open(os.path.join(FILE_PATH, 'anc.yml'), encoding="utf-8") as f:
            file_content = f.read()
        cls.anc = yaml.load(file_content, Loader=FullLoader)
        # Values for all profiles
        base_values = cls.anc.pop("base")
        for profile_name in cls.anc.keys():
            nutrients = cls.anc[profile_name]["nutrients"] + base_values
            nutrients_dict = dict((n['key'], n) for n in nutrients)
            assert len(nutrients_dict) == len(nutrients), "non-unique nutrient key in anc.yml"
            cls.anc[profile_name]["nutrients"] = nutrients_dict


    @classmethod
    def used_nutrient_ids(cls):
        from nutrient.models      import Nutrient
        nutrient_ids = set()
        for item in Config.anc.values():
            for nutri_desc in item['nutrients'].values():
                nutrient_ids.add(Nutrient.objects.get(name=nutri_desc['name']).id)
        for calculated_nutrient in cls.nutrient_calculations:
            nutrient_ids.add(Nutrient.objects.get(name=calculated_nutrient['name']).id)
        return nutrient_ids

    if TESTING :
        nutrient_calculations = []
    else:
        with open(os.path.join(FILE_PATH, 'nutrient_calculations.yml'), encoding="utf-8") as f:
            file_content = f.read()
        nutrient_calculations = yaml.load(file_content, Loader=FullLoader)

    with open(os.path.join(FILE_PATH, 'energy_conversion.yml'), encoding="utf-8") as f:
        file_content = f.read()
    __tmp_e_conv = yaml.load(file_content, Loader=FullLoader)
    energy_conversion = {}
    for category, infos in __tmp_e_conv.items():
        for nutrient in infos['nutrients']:
            energy_conversion[nutrient] = infos['kcal_per_g']

Config.load_anc()


# User.budget =>  (max average recipe price, max absolute recipe price)
# Recipe price is included in [1, 5]
BUDGET_VALUES = {
    1: {"max_avg": 2, "max_filter": 3},
    2: {"max_avg": 3, "max_filter": 4},
    3: {"max_avg": 4, "max_filter": 0}, # 0 == No max
}

# User.meat_level  =>  min/max per day (g) + daily tolerance min, daily tolerance max (%)
MEAT_LEVELS = {1: (0, 10, 1.0),
               2: None,  # No constraint
               3: (200, -1, 0.2)}

# User.fish_level  =>  min/max per day (g) + daily tolerance min, daily tolerance max (%)
FISH_LEVELS = {1: (0, 30, 1.0),
               2: None,  # No constraint
               3: (100, -1, 0.2)}