"""
Nutrients categorized
"""

NUTRIENT_CATEGORIES = {
    "vitamins": {
        'caption': "Vitamines",
        'indicators': [
            {'key': 'vitaminea',       'caption': "A"},
            {'key': 'vitamineb1',      'caption': "B1"},
            {'key': 'vitamineb2',      'caption': "B2"},
            {'key': 'vitamineb5',      'caption': "B5"},
            {'key': 'vitamineb6',      'caption': "B6"},
            {'key': 'vitamineb9',      'caption': "B9"},
            {'key': 'vitamineb12',     'caption': "B12"},
            {'key': 'vitaminec',       'caption': "C"},
            {'key': 'vitamined',       'caption': "D"},
            {'key': 'vitaminee',       'caption': "E"},
            {'key': 'vitamin_k',       'caption': "K"},
            {'key': 'betacarotene',    'caption': "BE"},
        ]
    },
   "minerals": {
        'caption': "Minéraux",
        'indicators': [
            {'key': 'fer',             'caption': "Fe"},
            {'key': 'magnesium',       'caption': "Mg"},
            {'key': 'calcium',         'caption': "Ca"},
            {'key': 'cuivre',          'caption': "Cu"},
            {'key': 'zinc',            'caption': "Zn"},
            {'key': 'phosphore',       'caption': "P"},
            {'key': 'potassium',       'caption': "K"},
            {'key': 'iode',            'caption': "I"},
            {'key': 'selenium',        'caption': "Se"},
        ]
    },
   "balance": {
        'caption': "Equilibre",
        'indicators': [
            {'key': 'energiekilocalories',        'caption': "calories"},
            {'key': 'sucrestotaux',               'caption': "sucre"},
            {'key': 'sodium',                     'caption': "sel"},
            {'key': 'proteines',                  'caption': "protéines"},
            {'key': 'lipides',                    'caption': "lipides"},
            {'key': 'acidesgrasnocifs',           'caption': "mauvaises graisses"},
            {'key': 'acidesgrassatures',          'caption': "graisses saturées"},
            {'key': 'agmonoinsatures',            'caption': "AG mono-insaturés"},
            {'key': 'fibres',                     'caption': "fibres"},
            {'key': 'cholesterol',                'caption': "cholesterol"},
            {'key': 'alcool',                     'caption': "alcool"},
        ]
    },
   "omega": {
        'caption': "Omegas",
        'indicators': [
            {'key': 'omega3dha',        'caption': "DHA"},
            {'key': 'omega3ala',        'caption': "ALA"},
            {'key': 'epadha',           'caption': "EPA+DHA"},
            {'key': 'omega6',           'caption': "Omega 6"},
            {'key': 'omega3',           'caption': "Omega 3"},
        ]
    }
}