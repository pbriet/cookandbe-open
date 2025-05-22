#!/usr/bin/env python
from bases.op_darwin_base_quality import BaseDarwinQuality

class DarwinQuality(BaseDarwinQuality):
    CATEGORY_SIZE = 200
    NB_CATEGORIES = 5  # + 1 which is "more_than_max"
    SCORE_TYPE = 'total_score'
    TITLE = "Darwin distribution of score (last week)"

DarwinQuality().apply()