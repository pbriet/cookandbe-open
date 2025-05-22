# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations

REPLACE_FOOD = {
    # Confitures
    "Confiture d'abricot": "Confiture ou Marmelade, tout type",
    "Confiture de cerise": "Confiture ou Marmelade, tout type",
    "Confiture de fraise": "Confiture ou Marmelade, tout type",
    "Confiture de framboise": "Confiture ou Marmelade, tout type",
    "Confiture de myrtilles": "Confiture ou Marmelade, tout type",
    "Confiture ou Marmelade d'orange": "Confiture ou Marmelade, tout type",
    "Confiture allégée en sucre, tout type": "Confiture ou Marmelade, tout type",
    # Beurre
    "Beurre allégé": "Beurre doux",
    "Beurre léger, 39-41% MG": "Beurre doux",
    "Beurre allégé, 60-62% MG": "Beurre doux",
    "Beurre léger, 39-41% MG, demi-sel": "Beurre demi-sel",
    "Beurre allégé, 60-62% MG, demi-sel": "Beurre demi-sel",
    # Lait
    "Lait écrémé, UHT": "Lait demi-écrémé, UHT",
    "Lait entier, UHT": "Lait demi-écrémé, UHT",
    "Lait entier, pasteurisé": "Lait demi-écrémé, UHT",
    "Lait écrémé, pasteurisé": "Lait demi-écrémé, UHT",
    "Lait demi-écrémé, pasteurisé": "Lait demi-écrémé, UHT",
    # Yaourt à boire
    "Yaourt à boire, au lait demi-écrémé, aux édulcorants": "Yaourt à boire",
    # Yaourt nature
    "Yaourt nature au lait entier": "Yaourt ou spécialité laitière nature",
    "Yaourt au lait entier, nature, brassé": "Yaourt ou spécialité laitière nature",
    "Spécialité laitière ou yaourt 0%, nature": "Yaourt ou spécialité laitière nature",
    "Yaourt au lait partiellement écrémé, nature": "Yaourt ou spécialité laitière nature",
    # Yaourt nature sucré
    "Yaourt au lait entier, nature, sucré": "Yaourt au lait partiellement ou demi-écrémé, nature, sucré",
    # Yaourt au fruits
    "Yaourt au lait entier, aromatisé, sucré": "Yaourt ou spécialité laitière aux fruits",
    "Yaourt au lait entier, aux fruits, sucré": "Yaourt ou spécialité laitière aux fruits",
    "Spécialité laitière ou yaourt 0%, aux fruits, sucrée": "Yaourt ou spécialité laitière aux fruits",
    "Spécialité laitière ou yaourt 0%, aromatisée, sucrée": "Yaourt ou spécialité laitière aux fruits",
    "Yaourt au lait partiellement écrémé, aromatisé, sucré": "Yaourt ou spécialité laitière aux fruits",
    "Spécialité laitière ou yaourt 0%, aux fruits, édulcoré": "Yaourt ou spécialité laitière aux fruits",
    "Yaourt au lait partiellement écrémé, aux fruits, sucré": "Yaourt ou spécialité laitière aux fruits",
    # Pâtes
    "Pâtes alimentaires aux oeufs": "Pâtes alimentaires",
    "Pâtes alimentaires au blé complet": "Pâtes alimentaires",
    "Pâtes alimentaires aux oeufs frais": "Pâtes alimentaires",
    # Farine
    "Farine de blé tendre ou froment T110": "Farine de blé T80",
    # Crème fraiche épaisse
    "crème fraiche légère 8% MG": "Crème fraîche épaisse (>= 30% MG)",
    "Crème fraîche légère 15-20% MG, épaisse": "Crème fraîche épaisse (>= 30% MG)",
    # Boissons
    "Café, poudre soluble": "Café noir",
    "Soda au cola, à teneur réduite en sucre": 'Soda au cola, "light"',
    # Vinaigrette
    "Sauce vinaigrette (50 à 75% d'huile)": "Sauce vinaigrette à l'huile d'olive (50 à 75% d'huile)",
    "Sauce vinaigrette allégée en MG (25 à 50% d'huile)": "Sauce vinaigrette à l'huile d'olive (50 à 75% d'huile)",
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
    "Poivron vert": "Poivron, vert, jaune ou rouge",
    "Poivron rouge": "Poivron, vert, jaune ou rouge",
    "Poivron jaune": "Poivron, vert, jaune ou rouge",
}

DISABLE_FOOD = {
    "Yaourt au lait de chèvre partiellement écrémé, nature",
    "Yaourt ou spécialité laitière nature ou aux fruits",
    "Spécialité laitière ou yaourt 0%, aux céréales ou muesli",
    "Yaourt ou lait fermenté au bifidus, au lait entier, aux céréales et/ou muesli",
    "Lait en poudre, entier",
    "Lait en poudre, écrémé",
    "Lait en poudre, demi-écrémé",
    "Lait de croissance infantile",
    "Crème de lait",
    "Lait concentré sucré, entier",
    "Lait concentré non sucré, entier",
    "Lait de poule, sans alcool",
    "Pâtes à la bolognaise (spaghetti, tagliatelles)",
    "Salade de pâtes, végétarienne",
    "Pâtes à la carbonara",
    "Gratin de pâtes",
    "Pain complet ou intégral (à la farine T150)",
    "Farine petit déjeuner bébé",
    "Céréales pour petit déjeuner",
    "Chocolat au lait aux céréales croustillantes, tablette",
    "Céréales chocolatées - non fourrées - enrichies en vitamines et minéraux",
    "Multi-céréales soufflées ou extrudées, enrichies en vitamines et minéraux",
    'Barre céréalière à base de céréales pour petit déjeuner et de lait, enrichie en vitamines et minéraux',
    "Muesli floconneux aux fruits ou fruits secs, sans sucre ajouté",
    "Muesli croustillant au chocolat, enrichi en vitamines et minéraux",
    "Muesli floconneux aux fruits ou fruits secs, enrichi en vitamines et minéraux",
    "Muesli croustillant aux fruits ou fruits secs, enrichi en vitamines et minéraux",
    "Café soluble reconstitué, non sucré",
    "Café décaféiné, soluble reconstitué, non sucré",
    "Café au lait, café crème ou cappuccino, non sucré",
    "Chicorée et café, poudre soluble",
    "Museau de porc vinaigrette",
    "Mayonnaise allégée en matière grasse",
    "Mayonnaise à l'huile de tournesol",
    "Crudité, sans assaisonnement",
    "Crudité vinaigrette",
    "Gâteau au fromage blanc",
}

RENAME_FOOD = {
    "Yaourt à boire, au lait demi-écrémé ou partiellement écrémé, aux fruits, sucré": "Yaourt à boire aux fruits",
    "Yaourt à boire": "Yaourt à boire nature",
    "Yaourt ou spécialité laitière nature": "Yaourt nature",
    "Yaourt au lait partiellement ou demi-écrémé, nature, sucré": "Yaourt nature sucré",
    "Yaourt ou spécialité laitière aux fruits": "Yaourt aux fruits",
    "Confiture ou Marmelade, tout type": "Confiture",
    "Lait demi-écrémé, UHT": "Lait",
    "Lait de poule, sans alcool": "Lait de poule",
    "Lait de chèvre, entier, UHT": "Lait de chèvre",
    "Lait de brebis, entier": "Lait de brebis",
    "Pâtes alimentaires": "Pâtes",
    "Farine de blé T55 (pour pains)": "Farine",
    "Farine de blé T80": "Farine demi-complète",
    "Farine de blé tendre ou froment T150": "Farine complète",
    "Farine de seigle T130": "Farine de seigle",
    "Crème fraîche épaisse (>= 30% MG)": "Crème fraîche épaisse",
    "Eau du robinet": "Eau",
    "Poivre noir, moulu": "Poivre",
    "Boules de maïs soufflées au miel, enrichies en vitamines et minéraux": "Céréales au maïs soufflé (Miel Pops, ...)",
    "Riz soufflé nature, enrichi en vitamines et minéraux": "Céréales au riz soufflé",
    "Riz soufflé au chocolat, enrichi en vitamines et minéraux": "Céréales au riz soufflé au chocolat (Coco Pops, Choco Pops, ...)",
    "Grains de blé soufflés chocolatés, enrichis en vitamines et minéraux": "Céréales au blé soufflé chocolatés",
    "Grains de blé soufflés au miel ou caramel, enrichis en vitamines et minéraux": "Céréales au blé soufflé au miel (Smacks, ...)",
    "Céréales pour petit déjeuner fourrées, fourrage autre que chocolat, enrichies en vitamines et minéraux": "Céréales fourrées",
    "Céréales pour petit déjeuner fourrées au chocolat ou chocolat-noisettes, enrichies en vitamines et minéraux": "Céréales fourrées au chocolat (Trésor, ...)",
    "Pétales de blé chocolatés, enrichis en vitamines et minéraux": "Céréales aux pétales de blé chocolatés (Chocapic, ...)",
    "Pétales de maïs natures, enrichis en vitamines et minéraux": "Céréales aux pétales de maïs (Corn Flakes, ...)",
    "Pétales de maïs glacés au sucre, enrichis en vitamines et minéraux": "Céréales aux pétales de maïs glacés au sucre (Frosties, ...)",
    'Céréales pour petit déjeuner riches en fibres, enrichies en vitamines et minéraux': "Céréales riches en fibres (All Bran, Fruits & Fibres, Weetabix, ...)",
    'Céréales pour petit déjeuner "équilibre" nature, enrichies en vitamines et minéraux': "Céréales allégées nature (Spécial K, Fitness, ...)",
    'Céréales pour petit déjeuner "équilibre" aux fruits, enrichies en vitamines et minéraux': "Céréales allégées aux fruits (Spécial K, Fitness, ...)",
    'Céréales pour petit déjeuner "équilibre" au chocolat, enrichies en vitamines et minéraux': "Céréales allégées au chocolat (Spécial K, Fitness, ...)",
    "Café décaféiné, non sucré": "Café décaféiné",
    "Café expresso, non sucré": "Café expresso",
    "Chicorée, poudre soluble": "Chicorée (poudre soluble)",
    "Thé infusé, non sucré": "Thé noir",
    "Tisane infusée, non sucrée": "Tisane ou thé vert",
    "Boisson au thé, aromatisée, sucrée": "Thé glacé (Ice Tea, Nestea, ...)",
    'Boisson au thé, aromatisée, "light"': "Thé glacé allégé (Ice Tea light, Nestea light, ...)",
    'Soda au cola, sucré': "Soda au cola (Coca cola, Pepsi, ...)",
    'Soda au cola, "light"': "Soda au cola allégé (Coca cola light, Pepsi light, ...)",
    'Noix de coco, "lait"': "Lait de noix de coco",
    'Noix de coco, eau': "Jus de coco (eau de noix de coco)",
    "Sauce vinaigrette à l'huile d'olive (50 à 75% d'huile)": "Vinaigrette",
    "Poivron, vert, jaune ou rouge": "Poivron",
}

USUALLY_STORED_FOODTYPES = {
    "Épices et fines herbes",
    "Matières grasses et huiles",
    "Matières grasses",
    "Boissons alcoolisées",
    "Confitures",
    "Café, thé, infusions, boissons au cacao",
    "Liqueurs et alcools",
    "Beurres et matières grasses laitières",
    "Sauces salées et condiments",
}

def remplaceRedundantIngredient(apps, schema_editor):
    Ingredient  = apps.get_model("recipe_mgr", "Ingredient")
    Food        = apps.get_model("recipe_mgr", "Food")

    oldToNewFood = dict()
    for oldFoodStr, newFoodStr in REPLACE_FOOD.items():
        oldFood = Food.objects.get(name = oldFoodStr)
        oldFood.enabled = False
        oldFood.save()
        oldToNewFood[oldFood.id] = Food.objects.get(name = newFoodStr)

    for ingredient in Ingredient.objects.filter(food_id__in = oldToNewFood.keys(), recipe__internal = False):
        ingredient.food_id = oldToNewFood[ingredient.food_id].id
        ingredient.save()

def normalizeFood(apps, schema_editor):
    Ingredient  = apps.get_model("recipe_mgr", "Ingredient")
    Food        = apps.get_model("recipe_mgr", "Food")
    
    for disabledFoodName in DISABLE_FOOD:
        food = Food.objects.get(name = disabledFoodName)
        food.enabled = False
        food.save()
    for water_bottle in Food.objects.filter(name__icontains = "embouteillée"):
        food.enabled = False
        food.save()
    for oldFoodName, newFoodName in RENAME_FOOD.items():
        food = Food.objects.get(name = oldFoodName)
        food.name = newFoodName
        food.save()

def fixUsuallyStored(apps, schema_editor):
    FoodType = apps.get_model("recipe_mgr", "FoodType")
    
    for food_type_name in USUALLY_STORED_FOODTYPES:
        food_type = FoodType.objects.get(name = food_type_name)
        food_type.usually_stored = True
        food_type.save()

class Migration(migrations.Migration):

    dependencies = [
        ('recipe_mgr', '0003_auto_20150709_1941'),
    ]

    operations = [
        # migrations.RunPython(remplaceRedundantIngredient),
        # migrations.RunPython(normalizeFood),
        # migrations.RunPython(fixUsuallyStored),
    ]
