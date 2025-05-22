from rest_framework.decorators      import api_view, permission_classes
from rest_framework.response        import Response

from optalim.settings               import DJANGO_PATH
from optalim.mongo                  import Mongo

from common.boost                       import to_dict
from common.permissions             import Allow
from common.decorators              import api_arg
from common.date                    import get_tomorrow
from common.math                    import pearson_correlation

from hippocrate.views.api           import suggest as api_suggest
from hippocrate.controls.generate   import optimize_days

from planning_mgr.controller.planning import build_planning,\
                                             get_planning_including_day_full_prefetch

from collections                    import defaultdict
from django.utils                   import timezone

import os, datetime, yaml

BENCHMARK_PATH = os.path.join(DJANGO_PATH, "hippocrate", "benchmark")

@api_view(['GET'])
@permission_classes((Allow('developer'),))
@api_arg('nb', int, 10)
def darwin_time_logs(request, nb):
    table = Mongo.log_table("darwin_times")
    cursor = table.find({}, {'_id': False}).sort("_id", -1).limit(nb)
    return Response({"entries": list(cursor)})


@api_view(['GET'])
@permission_classes((Allow('developer'),))
def darwin_benchmark(request):
    """
    Return the data contained in the benchmark files  (for debugging)
    """
    res = []
    for filename in sorted(os.listdir(BENCHMARK_PATH), reverse=True):
        if filename.startswith("darwin_score_") and filename.endswith(".yml"):
            filepath = os.path.join(BENCHMARK_PATH, filename)
            with open(filepath) as f:
                data = yaml.load(f)
            time_str = data['time'].strftime('%Y-%m-%d_%Hh%Mm%Ss')
            if time_str in filename:
                # This is an anonymous benchmark. Use time as title
                data['title'] = data['time'].strftime('%d/%m %H:%M')
            else:
                # Use filename as title
                data['title'] = filename.replace('darwin_score_', '').replace('.yml', '').replace("_", " ").strip()
            res.append(data)
    return Response(res, 200)

@api_view(['POST'])
@permission_classes((Allow('developer'),))
def darwin_clean_logs(request):
    nb_deletions = 0
    for filename in sorted(os.listdir(BENCHMARK_PATH), reverse=True):
        if filename.startswith("darwin_") and filename.endswith(".yml"):
            filepath = os.path.join(BENCHMARK_PATH, filename)
            os.remove(filepath)
            nb_deletions += 1
    return Response({ "deletions": nb_deletions }, 200)
    
@api_view(['POST'])
@permission_classes((Allow('developer'),))
def darwin_batch_results(request):
    call_stats_sum = defaultdict(int)
    batch_constraint_tautness = defaultdict(list)
    batch_day_constraint_interval = None
    batch_week_constraint_interval = None
    batch_recipes_redundancy = defaultdict(int)
    nb_favorites_recipes = {"distinct": [], "all": []}
    nb_batch = 0
    for filename in sorted(os.listdir(BENCHMARK_PATH), reverse=True):
        if filename.startswith("darwin_batch_") and filename.endswith(".yml"):
            filepath = os.path.join(BENCHMARK_PATH, filename)
            with open(filepath) as f:
                data = yaml.load(f)
            for stat, time in data["call_stats"].items():
                call_stats_sum[stat] += time
            for key, value in data["favorite_recipes"].items():
                nb_favorites_recipes[key].append(value)
                
            for constraint, penalty in data["constraint_tautness"].items():
                assert len(batch_constraint_tautness[constraint]) == nb_batch, "Inconsistant constraint stats : " + str(batch_constraint_tautness[constraint])
                batch_constraint_tautness[constraint].append(penalty)
           
            for constraint, wData in data["week_constraint_intervals"].items():
                wMin, wMax, wValue  = wData
                if batch_week_constraint_interval is None:
                    batch_week_constraint_interval = dict((c, {"min": min, "max": max, "values": []}) for c, (min, max, value) in data["week_constraint_intervals"].items())
                
                dData = data["day_constraint_intervals"].get(constraint, None)
                
                assert constraint in batch_week_constraint_interval, "Inconsistant constraint %s" % constraint
                assert len(batch_week_constraint_interval[constraint]["values"]) == nb_batch, "Inconsistant constraint interval : " + str(batch_week_constraint_interval[constraint])
                assert batch_week_constraint_interval[constraint]["min"] == wMin,  "Inconsistant constraint interval min : %i != %i" % (batch_week_constraint_interval[constraint]["min"], wMin)
                assert batch_week_constraint_interval[constraint]["max"] == wMax,   "Inconsistant constraint interval max : %i != %i" % (batch_week_constraint_interval[constraint]["max"], wMax)
                if dData:
                    dMin, dMax, dValues  = dData
                    if batch_day_constraint_interval is None:
                        batch_day_constraint_interval = dict((c, {"min": min, "max": max, "values": []}) for c, (min, max, values) in data["day_constraint_intervals"].items())
            
                    assert batch_day_constraint_interval[constraint]["max"] == dMax,    "Inconsistant constraint interval max : %i != %i" % (batch_day_constraint_interval[constraint]["max"], dMaw)
                    assert batch_day_constraint_interval[constraint]["min"] == dMin,   "Inconsistant constraint interval min : %i != %i" % (batch_day_constraint_interval[constraint]["min"], dMin)
                    assert len(batch_day_constraint_interval[constraint]["values"]) == nb_batch * 7, "Inconsistant constraint interval : " + str(batch_day_constraint_interval[constraint])
                    assert constraint in batch_day_constraint_interval, "Inconsistant constraint %s" % constraint
                    
                    batch_day_constraint_interval[constraint]["values"] += dValues
                    
                batch_week_constraint_interval[constraint]["values"].append(wValue)
                        
            nb_batch += 1
            for dish_type_id, recipes in data["best_recipes_per_dishtype"].items():
                if dish_type_id in (2, 3, 4, 5):
                    for recipe_id in recipes:
                        batch_recipes_redundancy[recipe_id] += 1
                        
    # Reformating
    call_stats_avg = dict((stat, total_time / nb_batch) for stat, total_time in call_stats_sum.items())
    return Response({
        "call_stats_avg": call_stats_avg,
        "batch_constraint_tautness": dict(batch_constraint_tautness.items()),
        "batch_day_constraint_interval": batch_day_constraint_interval,
        "batch_day_nutrient_correlations": compute_2D_nutrient_correlations(batch_day_constraint_interval),
        "batch_week_constraint_interval": batch_week_constraint_interval,
        "batch_recipes_redundancy": batch_recipes_redundancy,
        "nb_favorites_recipes": nb_favorites_recipes
    }, 200)

def compute_2D_nutrient_correlations(day_constraint_intervals):
    res = []
    if day_constraint_intervals is None:
        return res
    constraints = list(day_constraint_intervals.keys())
    for i, left in enumerate(constraints):
        for j in range(i + 1, len(constraints)):
            right = constraints[j]
            res.append([left, right, pearson_correlation(day_constraint_intervals[left]["values"], day_constraint_intervals[right]["values"])])
    return res

def calc_favorite_recipes(problem, solution):
    """
    Return the number of favorite recipes stored in days
    """
    favorite_ids = problem.favorite_recipe_ids
    
    res = []
    
    dish_id_to_dishrecipes = to_dict(solution.get_dish_recipes())
    dish_recipe_objects = []
    for dish_id, cpp_dishrecipes in dish_id_to_dishrecipes.items():
        for i, cpp_dishrecipe in enumerate(cpp_dishrecipes):
            recipe_id = cpp_dishrecipe.recipe.recipe_id
            if recipe_id in favorite_ids:
                res.append(recipe_id)
            
    return res

@api_view(['POST'])
@permission_classes((Allow('developer'),))
@api_arg('nb_batch', int, 10)
def darwin_batch_run(request, nb_batch):
    print("### Starting %i darwin batch ###" % nb_batch)
    date = get_tomorrow()
    assert 1 <= nb_batch <= 100, "Invalid batch number"
    for n in range(nb_batch):
        data = {}
        # Rebuilding one week from the given day
        build_planning(request.user, date, 7)
        days = get_planning_including_day_full_prefetch(request.user, date)
        problem, solution = optimize_days(days, "darwin", start_from_existing_solution = False)
        data["call_stats"]                  = dict((item.key(), item.data().total_time) for item in iter(problem.darwin_call_stats))
        data["constraint_tautness"]         = dict((item.key(), item.data()) for item in iter(problem.darwin_constraint_tautness))
        data["population_variation_score"]  = dict((item.key(), item.data()) for item in iter(problem.darwin_population_variation_score))
        data["best_recipes_per_dishtype"]   = dict((item.key(), list(iter(item.data()))) for item in iter(problem.darwin_best_recipes_per_dishtype))
        data["day_constraint_intervals"], data["week_constraint_intervals"] = problem.get_constraint_intervals(solution)
        favorite_recipes = calc_favorite_recipes(problem, solution)
        data["favorite_recipes"]            = {"distinct": len(set(favorite_recipes)), "all": len(favorite_recipes)}
        filename = "darwin_batch_%s.yml" % timezone.now().strftime('%Y-%m-%d_%Hh%Mm%Ss')
        filepath = os.path.join(BENCHMARK_PATH, filename)
        print("Writing results in %s" % filename)
        with open(filepath, "w") as f:
            yaml.dump(data, f)
    return Response({}, 200)
