#!/usr/bin/env python
from bases.op_darwin_base_quality import BaseDarwinQuality

class DarwinNutrientQuality(BaseDarwinQuality):
    CATEGORY_SIZE = 200
    NB_CATEGORIES = 5  # + 1 which is "more_than_max"
    SCORE_TYPE = 'nutrient_score'
    TITLE = "Darwin distribution of nutrient score (last week)"

DarwinNutrientQuality().apply()