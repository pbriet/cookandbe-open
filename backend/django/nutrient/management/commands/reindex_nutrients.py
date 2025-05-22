from django.core.management.base import BaseCommand, CommandError
from nutrient.models             import Nutrient
from optalim.config              import Config
import copy
"""
This scripts reindex nutrients by putting the ones used in ANC with low indexes
"""

# Iterates on the lowest ids available in the Nutrient table
class LowIdIterator(object):
    def __init__(self):
        self.value = 0
        self.next()

    def next(self):
        while(1):
            self.value += 1
            if Nutrient.objects.filter(pk=self.value).count() == 0:
                break

class Command(BaseCommand):
    args = ''
    help = 'Reindexes nutrients by putting the ones used in ANC with low indexes'

    def handle(self, *args, **options):

        # We select only the nutrients used in constraints
        nutrients = set()
        for item in Config.anc.values():
            for nutri_desc in item['nutrients']:
                nutrients.add(Nutrient.objects.get(name=nutri_desc['name']))

        id_iterator = LowIdIterator()

        # We decide what will be the future ids. previous id --> new id
        nutrient_future_ids = {}
        for nutrient in nutrients:
            if nutrient.id > max(len(nutrients) + 1, id_iterator.value):
                # Ok, we have a nutrient with an id that could be lower
                # Let's reindex it
                nutrient_future_ids[nutrient.id] = id_iterator.value
                id_iterator.next()

        print("Reindexing %i nutrients..." % len(nutrient_future_ids))

        for old_nutrient_id, new_nutrient_id in nutrient_future_ids.items():
            nutrient = Nutrient.objects.get(pk=old_nutrient_id)
            print("* %s" % nutrient.name)
            nutrient.id = new_nutrient_id
            nutrient.save() # Copy

            # We iterate on all the related fields
            for rel in Nutrient._meta.get_all_related_objects():
                model_cls = rel.model  # FoodNutrient
                field_name = rel.field.name  # nutrient  (FoodNutrient.nutrient)

                # nutrient__id = <value>
                query_kwargs = {'%s__id' % (field_name): old_nutrient_id}
                # Iterating on related objects
                for obj in model_cls.objects.filter(**query_kwargs):
                    # Modifying id
                    setattr(obj, "%s_id" % field_name, new_nutrient_id)
                    obj.save()

            nutrient = Nutrient.objects.get(pk=old_nutrient_id)
            nutrient.delete() # Remove the original nutrient