// Details on speed options  (numeric, from 1 to 4)
export const HABITS_SPEED_OPTIONS = [
  { id: 1, label: "Express (< 10 min)", shortLabel: "Express" },
  { id: 2, label: "Rapide (< 15 min)", shortLabel: "Rapide" },
  { id: 3, label: "Normal (< 30 min)", shortLabel: "Normal" },
  { id: 4, label: "Libre", shortLabel: "Libre" },
];

// Details on recipe cooking difficulty [1 : 5]
export const RECIPE_DIFFICULTY_OPTIONS = [
  { id: 1, label: "Très facile" },
  { id: 2, label: "Facile" },
  { id: 3, label: "Moyen" },
  { id: 4, label: "Difficile" },
  { id: 5, label: "Chef" },
];

// Details on recipe shopping price [1 : 5]
export const RECIPE_PRICE_OPTIONS = [
  { id: 1, label: "Economique" },
  { id: 2, label: "Bon marché" },
  { id: 3, label: "Abordable" },
  { id: 4, label: "Assez chère" },
  { id: 5, label: "Très chère" },
];

// Dictionary id => label
export const RECIPE_PRICE_OPTIONS_DICT = {};
for (let i = 0; i < RECIPE_PRICE_OPTIONS.length; i++) {
  const val = RECIPE_PRICE_OPTIONS[i];
  RECIPE_PRICE_OPTIONS_DICT[val.id] = val.label;
}

// Details on recipe cooking speed [1 : 5]
export const RECIPE_SPEED_OPTIONS = [
  { id: 1, label: "Express" },
  { id: 2, label: "Rapide" },
  { id: 3, label: "Modéré" },
  { id: 4, label: "Long" },
  { id: 5, label: "Très long" },
];

// Dictionary id => label
export const RECIPE_SPEED_OPTIONS_DICT = {};
for (let i = 0; i < RECIPE_SPEED_OPTIONS.length; i++) {
  const val = RECIPE_SPEED_OPTIONS[i];
  RECIPE_SPEED_OPTIONS_DICT[val.id] = val.label;
}

// Meta Descriptions
export const RECIPE_META_DESC_DIFFICULTY = [
  "très facile",
  "facile",
  "de difficulté moyenne",
  "difficile",
  "très difficile",
];
export const RECIPE_META_DESC_PRICE = ["économique", "bon marché", "abordable", "assez chère", "très chère"];
export const RECIPE_META_DESC_SPEED = [
  "express",
  "rapide",
  "assez rapide",
  "longue à préparer",
  "très longue à préparer",
];

export const RECIPE_STATUS = [
  { id: 0, label: "Créée" },
  { id: 1, label: "Validée" },
  { id: 2, label: "Revue" },
  { id: 3, label: "Publiée" },
];

// Pictures and label for places
export const PLACES = {
  home: {
    img: "place/home.png",
    key: "home",
    label: "Repas préparé à la maison",
    shortLabel: "A la maison",
  },
  // "lunchpack": {
  //   "img"         : 'place/lunchpack.png',
  //   "key"         : 'lunchpack',
  //   "label"       : "Repas préparé à emporter",
  //   "shortLabel" : "A emporter",
  // },
  away: {
    img: "place/restaurant.png",
    key: "away",
    label: "Repas pris à l'extérieur",
    shortLabel: "A l'extérieur",
  },
  donoteat: {
    img: "place/donoteat.png",
    key: "donoteat",
    label: "Ne mange pas à ce repas",
    shortLabel: "Ne mange pas",
  },
};

// Special id for food which is not actual food (aluminum paper for instance)
export const COOKING_CONSUMER_GOODS_FOOD_TYPE_ID = 119;

// Name used when creating a new recipe
export const DEFAULT_RECIPE_NAME = "Nouvelle recette";

// Text used when a recipe has no instructions
export const DEFAULT_RECIPE_INSTRUCTION = "Dégustez !";

// How many characters to start a research
export const RECIPE_SEARCH_DEFAULT_MIN_CHARS = 3;

// cock-a-doodle-doo
export const FRANCE_LOCATION_ID = 208;

export const SERVER_DOWN_MESSAGE =
  "Nos serveurs d'authentification sont actuellement indisponibles, merci de réessayer dans quelques minutes";

export const RATING_DESCRIPTION = {
  null: "Non définie",
  1: "Mauvais",
  2: "Décevant",
  3: "Moyen",
  4: "Bon",
  5: "Excellent",
};

// Configuration stage icons
export const CONFIG_STAGE_ICONS = {
  user_profile: ["fas", "user"],
  attendance: ["fas", "home"],
  habits: ["fas", "coffee"],
  family: ["fas", "users"],
  meal_sharing: ["fas", "utensils"],
  tastes: ["far", "thumbs-down"],
  other: ["fas", "wrench"],
  equipment: ["fas", "blender"],
};

export const ROLE_ICONS = [
  { name: "admin", glyphicon: "tower" },
  { name: "author", glyphicon: "file" },
  { name: "moderator", glyphicon: "bullhorn" },
  { name: "reviewer", glyphicon: "eye-open" },
  { name: "operator", glyphicon: "wrench" },
  { name: "developer", glyphicon: "tasks" },
  { name: "dietician", fa: "stethoscope" },
  { name: "ordinary", glyphicon: "user" },
];

export function getRoleIconClass(roleName) {
  var icon = ROLE_ICONS.first({ name: roleName });

  if (!icon) {
    return "fa fa-question";
  }
  if (icon.glyphicon) {
    return "glyphicon glyphicon-" + icon.glyphicon;
  } else {
    return "fa fa-" + icon.fa;
  }
}

const BALANCED_RULES = {
  rules: [
    "Contrôle de l'équilibre lipides/glucides/protides",
    "Vérification des apports en 13 vitamines et 8 minéraux",
    "Vérification des apports en fibres, omégas 3 et 6",
  ],
  advices: ["Faites régulièrement une activité sportive", "Buvez 1.5L d'eau par jour"],
}

const SLIM_RULES = {
  rules: [
    "Maitrise de l'apport calorique",
    "Adaptation du régime en fonction de l'évolution du poids",
    "Des apports protidiques légèrement supérieurs",
  ],
  advices: [
    "Faites régulièrement une activité sportive",
    "Buvez 1.5L d'eau par jour",
    "Ne grignottez pas. Dans l'idéal, prenez 3 repas par jour.",
    "Faites de bonnes nuits de sommeil. Dormir aide à réguler la faim.",
  ],
}

const VEGETARIAN_RULES = {
  rules: [
    "Exclusion de la viande, du poisson et des crustacés",
    "Contrôle de vos apports en protéines végétales",
    "Maîtrise de l'équilibre sur 30 nutriments pour éviter les carences",
  ],
  advices: ["Faites régulièrement une activité sportive", "Buvez 1.5L d'eau par jour"],
}

const GLUTEN_FREE_RULES = {
  rules: [
    "Exclusion des aliments et recettes contenant du blé, du seigle, de l'orge ou de l'avoine",
    "Avertissement pour les aliments à surveiller car pouvant contenir des traces de gluten ou être contaminés",
    "Contrôle de l'équilibre sur 30 nutriments pour éviter les carences",
  ],
  advices: ["Faites régulièrement une activité sportive", "Buvez 1.5L d'eau par jour"],
}

export const DIET_INFOS = {
  balanced: BALANCED_RULES,
  slim: SLIM_RULES,
  easy_digest: {
    rules: [
      "Réduction des apports en lipides",
      "Exclusion des aliments à goût fort ou acides",
      "Exclusion des aliments provoquant des flatulences ou régurgitations",
      "Et tous les apports en vitamines, minéraux, omégas, fibres, ...",
    ],
    advices: [
      "Mangez lentement, en mastiquant bien",
      "Mangez en situation de calme : pas de télé, pas de stress !",
      "Buvez plutôt en dehors des repas",
      "Prenez des goûters et collations pour alléger les repas du midi et du soir",
    ],
  },
  vegetarian: VEGETARIAN_RULES,
  gluten_free: GLUTEN_FREE_RULES,
  hypertension: {
    rules: [
      "Les bons apports en sels",
      "Maîtrise des apports caloriques",
      "Et tous les apports en vitamines, minéraux, omégas, fibres, ...",
    ],
    advices: [
      "Limitez votre consommation de caféine : café, thé, cola, boisson énergisantes",
      "N'ajoutez pas de sel en plus de celui présent dans les préparations",
      "Pratiquez une activité sportive d'endurance",
      "Si vous avez des difficultés à gérer vos émotions, pratiquez des techniques de relaxation (yoga, méditation, sophrologie, Tai Chi, Qi Cong...)",
    ],
  },
  normolipidic: {
    rules: [
      "Limitation du cholestérol alimentaire et des graisses saturées",
      "Apports optimaux en acides gras essentiels (omégas 6, omégas 3...)",
      "Maîtrise des apports caloriques",
      "Et tous les apports en vitamines, minéraux, fibres, ...",
    ],
    advices: [
      "Supprimez le tabac",
      "Pratiquez une activité physique régulière favorise la baisse des taux de cholestérol",
      "Ne cherchez pas à avoir une alimentation trop stricte (suppression totale du fromage et du beurre etc.), les menus générés vous proposent des apports optimisés",
      //      "Pour les dames, vos hormones vous protègent pour partie d'un excès de cholestérol. Après la ménopause, vous vous retrouvez avec les mêmes risques que les hommes.",
    ],
  },
  diabete: {
    rules: [
      "Contrôle des apports en féculents, produits sucrés et alcool pour lisser la glycémie",
      "Maîtrise des apports caloriques",
      "Et tous les apports en vitamines, minéraux, omégas, fibres, ...",
    ],
    advices: [
      "Ne sautez jamais de repas, la régularité est très importante",
      "Ne consommez pas de produits sucrés en dehors des repas (bonbons, soda...)",
      'Mais soyez attentifs aux signes d\'hypoglycémie pour vous "resucrer" si nécessaire',
      "Pratiquez une activité physique adaptée à vos possibilités",
    ],
  },
};

export const MONTH_CAPTIONS = [
  "Janvier",
  "Février",
  "Mars",
  "Avril",
  "Mai",
  "Juin",
  "Juillet",
  "Août",
  "Septembre",
  "Octobre",
  "Novembre",
  "Décembre",
];
export const MONTH_CAPTIONS_IDS = [];
for (var i = 0; i < MONTH_CAPTIONS.length; i++) {
  MONTH_CAPTIONS_IDS.push({ id: i + 1, caption: MONTH_CAPTIONS[i] });
}

export const SUBSCRIPTION_NAMES = {
  0: "Gratuit",
  // 1: "Liberté",
  1: "Premium",
};

export const SUBSCRIPTION_DIET_CATEGORY = {
  1: "Bien-être",
  2: "Santé",
};

export const GCHART_COLORS = ["#7AB231", "#f4c741", "#d9534f", "#f0ad4e", "#d5a01d", "#f7f7f7"];
