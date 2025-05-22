from django.utils               import timezone

from optalim.mongo              import Mongo
from optalim.settings           import TESTING, ENABLE_MONGO_TESTING

import copy

def get_context_log(problem):
    """
    Returns true if this is a full planning generation
    """
    return {"some_dish_ids_only":            problem.dish_ids is not None,
            "make_validated_mutable":        problem.make_validated_mutable,
            "minimize_change":               problem.minimize_change,
            "start_from_existing_solution":  problem.start_from_existing_solution}


def save_darwin_started_log(problem):
    """
    Save in mongo an entry that says that the problem resolution has started.
    This is used to detect any anomalies  (C++ segfaults by example)
    """
    if TESTING and not ENABLE_MONGO_TESTING:
        return
    infos = {"date":      timezone.now(),
             "problem_key": id(problem),
             "user_id":   problem.user.id,
             'status':    'start'}

    crash_check = Mongo.log_table("crash_check")
    crash_check.insert_one(infos)

def save_darwin_finished_logs(problem):
    """
    Store the time logs into Mongo
    """
    if TESTING and not ENABLE_MONGO_TESTING:
        return
    context = get_context_log(problem)

    base_infos = {"date":      timezone.now(),
                  "problem_key": id(problem),
                  "user_id":   problem.user.id}

    time_table = Mongo.log_table("darwin_times")
    time_infos = copy.copy(base_infos)
    time_infos["context"] = context
    time_infos["values"] = problem.chronos
    time_table.insert_one(time_infos)

    crash_check = Mongo.log_table("crash_check")
    crash_infos = copy.copy(base_infos)
    crash_infos['status'] = 'end'
    crash_check.insert_one(crash_infos)

def save_constraint_logs(problem, solution, score):
    """
    Store in mongo stats about how constraints are respected or broken
    """

    if TESTING and not ENABLE_MONGO_TESTING:
        return
    context = get_context_log(problem)

    total_score = 0
    nutrient_score = 0
    broken_constraints = []
    for constraint in problem.py_constraints:
        constraint_score = constraint.cost(score)
        if constraint_score > 0:
            broken_constraints.append((constraint.key, constraint_score))
            total_score += constraint_score
            if constraint.is_nutrient_related():
                nutrient_score += constraint_score

    log_value = {"user_id": problem.user.id,
                 "date": timezone.now(),
                 "nutrient_score": nutrient_score,
                 "total_score": total_score,
                 "nb_filters": len(problem.py_filters),
                 "nb_constraints": len(problem.py_constraints),
                 "nb_broken_constraints": len(broken_constraints),
                 "broken_constraints": broken_constraints}

    quality_table = Mongo.log_table("darwin_quality")
    quality_table.insert_one(log_value)

