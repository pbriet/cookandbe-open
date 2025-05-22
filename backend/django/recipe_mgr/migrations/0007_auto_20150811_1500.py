# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


REPLACED_FOOD = {
    # Confitures
    "Confiture d'abricot": "Confiture",
    "Confiture de cerise": "Confiture",
    "Confiture de fraise": "Confiture",
    "Confiture de framboise": "Confiture",
    "Confiture de myrtilles": "Confiture",
    "Confiture ou Marmelade d'orange": "Confiture",
    "Confiture allégée en sucre, tout type": "Confiture",
    # Beurre
    "Beurre allégé": "Beurre doux",
    "Beurre léger, 39-41% MG": "Beurre doux",
    "Beurre allégé, 60-62% MG": "Beurre doux",
    "Beurre léger, 39-41% MG, demi-sel": "Beurre demi-sel",
    "Beurre allégé, 60-62% MG, demi-sel": "Beurre demi-sel",
    # Lait
    "Lait écrémé, UHT": "Lait",
    "Lait entier, UHT": "Lait",
    "Lait entier, pasteurisé": "Lait",
    "Lait écrémé, pasteurisé": "Lait",
    "Lait demi-écrémé, pasteurisé": "Lait",
    # Yaourt à boire
    "Yaourt à boire, au lait demi-écrémé, aux édulcorants": "Yaourt à boire nature",
    # Yaourt nature
    "Yaourt nature au lait entier": "Yaourt nature",
    "Yaourt au lait entier, nature, brassé": "Yaourt nature",
    "Spécialité laitière ou yaourt 0%, nature": "Yaourt nature",
    "Yaourt au lait partiellement écrémé, nature": "Yaourt nature",
    # Yaourt nature sucré
    "Yaourt au lait entier, nature, sucré": "Yaourt nature sucré",
    # Yaourt au fruits
    "Yaourt au lait entier, aromatisé, sucré": "Yaourt aux fruits",
    "Yaourt au lait entier, aux fruits, sucré": "Yaourt aux fruits",
    "Spécialité laitière ou yaourt 0%, aux fruits, sucrée": "Yaourt aux fruits",
    "Spécialité laitière ou yaourt 0%, aromatisée, sucrée": "Yaourt aux fruits",
    "Yaourt au lait partiellement écrémé, aromatisé, sucré": "Yaourt aux fruits",
    "Spécialité laitière ou yaourt 0%, aux fruits, édulcoré": "Yaourt aux fruits",
    "Yaourt au lait partiellement écrémé, aux fruits, sucré": "Yaourt aux fruits",
    # Pâtes
    "Pâtes alimentaires aux oeufs": "Pâtes",
    "Pâtes alimentaires au blé complet": "Pâtes",
    "Pâtes alimentaires aux oeufs frais": "Pâtes",
    # Farine
    "Farine de blé tendre ou froment T110": "Farine demi-complète",
    # Crème fraiche épaisse
    "crème fraiche légère 8% MG": "Crème fraîche épaisse",
    "Crème fraîche légère 15-20% MG, épaisse": "Crème fraîche épaisse",
    # Boissons
    "Café, poudre soluble": "Café noir",
    "Soda au cola, à teneur réduite en sucre": "Soda au cola allégé (Coca cola light, Pepsi light, ...)",
    # Vinaigrette
    "Sauce vinaigrette (50 à 75% d'huile)": "Vinaigrette",
    "Sauce vinaigrette allégée en MG (25 à 50% d'huile)": "Vinaigrette",
    # Fromage blanc
    "Fromage blanc battu 0% MG": "Fromage blanc nature ou aux fruits",
    "Fromage blanc battu au lait entier": "Fromage blanc nature ou aux fruits",
    "Fromage blanc campagne 0% MG nature": "Fromage blanc nature ou aux fruits",
    "Fromage blanc campagne au lait entier nature": "Fromage blanc nature ou aux fruits",
    "Fromage blanc battu au lait demi-écrémé nature": "Fromage blanc nature ou aux fruits",
    "Fromage blanc battu au lait partiellement écrémé nature": "Fromage blanc nature ou aux fruits",
    "Fromage blanc ou spécialité laitière, aromatisé ou aux fruits": "Fromage blanc nature ou aux fruits",
    "Fromage blanc battu 0% MG aux fruits, allégé en sucre, édulcoré": "Fromage blanc nature ou aux fruits",
    # Poivron
    "Poivron vert": "Poivron",
    "Poivron rouge": "Poivron",
    "Poivron jaune": "Poivron",
}


class Migration(migrations.Migration):

    dependencies = [
        ('recipe_mgr', '0006_dishtype_mono_recipe'),
    ]

    CACHED_CONVERSIONS_PER_FOOD = {}

    def retrieve_lost_conversions(apps, schema_editor):
        """
        We lost some conversion when "simplifying" foods (0004_ingredient_simplification)
        Re-retrieving them in the standardized food
        """
        Food = apps.get_model("recipe_mgr", "Food")
        
        for old_food_name, new_food_name in REPLACED_FOOD.items():
            old_food = Food.objects.prefetch_related('conversions').get(name=old_food_name)
            new_food = Food.objects.prefetch_related('conversions').get(name=new_food_name)
            
            existing_units = set(cnv.unit for cnv in new_food.conversions.all())
            existing_values = set(cnv.value for cnv in new_food.conversions.all())
            
            SKIPPED_CONVERSIONS = (("Poivron rouge", "petit"), ("Poivron jaune", "moyen poivron"),) 
            
            for old_cnv in old_food.conversions.all():
                if (old_food_name, old_cnv.unit) in SKIPPED_CONVERSIONS:
                    continue
                if old_cnv.unit not in existing_units and old_cnv.value not in existing_values:
                    # copying old conversion
                    print("* copying conversion %s, from %s to %s" % (old_cnv.unit, old_food_name, new_food_name))
                    old_cnv.id = None
                    old_cnv.food_id = new_food.id
                    old_cnv.save()
                    existing_values.add(old_cnv.value)
                    existing_units.add(old_cnv.unit)
        


    @classmethod
    def _get_conversions_per_food(cls, FoodConversion, food_id):
        if food_id not in cls.CACHED_CONVERSIONS_PER_FOOD:
            values = list(FoodConversion.objects.filter(food_id=food_id))
            cls.CACHED_CONVERSIONS_PER_FOOD[food_id] = values
        return cls.CACHED_CONVERSIONS_PER_FOOD[food_id]

    def fix_invalid_default_conversions(apps, schema_editor):
        """
        Conversions assigned to ingredient were not all compatible with the food
        """
        Ingredient = apps.get_model("recipe_mgr", "Ingredient")
        FoodConversion = apps.get_model("recipe_mgr", "FoodConversion")
        
        for ingredient in Ingredient.objects.prefetch_related('food', 'default_conversion'):
            if ingredient.default_conversion.food_id == ingredient.food_id:
                # All right, conversion belongs to food !
                continue
            #print("Fix conversion for %s" % ingredient.food.name)
            conversions = Migration._get_conversions_per_food(FoodConversion, ingredient.food_id)
            unit = ingredient.default_conversion.unit
            if ingredient.food.name == "Poivron" and unit == "petit":
                unit = "petit poivron"
            if ingredient.food.name == "Poivron" and unit == "moyen poivron":
                unit = "poivron"
            
            for conversion in conversions:
                if conversion.unit == unit or\
                conversion.value == ingredient.default_conversion.value:
                    break
            else:
                assert False, "conversion not found for %s (%s)" % (ingredient.food.name, unit)
           
            ingredient.default_conversion = conversion
            ingredient.save()
         
    operations = [
        # migrations.RunPython(retrieve_lost_conversions),
        # migrations.RunPython(fix_invalid_default_conversions)
    ]
