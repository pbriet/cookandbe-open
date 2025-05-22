export const INDICATOR_TITLE = {
  meal_balance: "Equilibre dîner/déjeuner",
  energiekilocalories: "Apport calorique",
  lipides: "Lipides",
  sucrestotaux: "Sucres",
  added_sugar: "Sucres ajoutés",
  proteines: "Protéines",
  fibres: "Fibres",
  // "omega6": "Oméga 6",
  // "omega3ala": "Oméga 3 ALA",
  // "omega3dha": "Oméga 3 DHA",
  // "epadha": "Oméga 3 EPA+DHA",
  sodium: "Sel",
  potassium: "Potassium",
  acidesgrasnocifs: "Acides gras athérogènes",
  acidesgrassatures: "Acides gras saturés",
  agmonoinsatures: "Acides gras mono-insaturés",
  vitaminec: "Vitamine C",
  vitamineb5: "Vitamine B5",
  vitamineb12: "Vitamine B12",
  vitaminee: "Vitamine E",
  vitamined: "Vitamine D",
  // "vitaminek": "Vitamine K",
  calcium: "Calcium",
  phosphore: "Phosphore",
  cuivre: "Cuivre",
  // "fluor": "Fluor",
  iode: "Iode",
  vitamineb1: "Vitamine B1",
  vitamineb3: "Vitamine B3",
  selenium: "Sélénium",
  // "betacarotene": "Béta carotène",
  vitamineb2: "Vitamine B2",
  vitamineb6: "Vitamine B6",
  vitamineb9: "Vitamine B9",
  vitaminea: "Vitamine A",
  magnesium: "Magnésium",
  fer: "Fer",
  zinc: "Zinc",
};

export const INDICATOR_GROUPS = [
  {
    title: "Macro-nutriments",
    indicators: [
      "energiekilocalories",
      "proteines",
      "lipides",
      "fibres",
      "agmonoinsatures",
      "acidesgrassatures",
      "acidesgrasnocifs",
      "sucrestotaux",
      "added_sugar",
    ],
  },
  {
    title: "Vitamines",
    indicators: [
      "vitaminea",
      "vitamineb1",
      "vitamineb2",
      "vitamineb3",
      "vitamineb5",
      "vitamineb6",
      "vitamineb9",
      "vitamineb12",
      "vitaminec",
      "vitamined",
      "vitaminee",
      // "betacarotene",//
    ],
  },
  {
    title: "Minéraux",
    indicators: [
      "sodium",
      "calcium",
      "magnesium",
      "fer",
      "potassium",
      "phosphore",
      "cuivre",
      "zinc",
      "selenium",
      "iode",
      // "vitaminek",
      // "fluor",
    ],
  },
  // "omega6",
  // "omega3ala",
  // "omega3dha",
  // "epadha"
];

export const INDICATOR_DESCRIPTION = {
  meal_balance: "Les apports caloriques du dîner se situent entre 70% et 100% du déjeuner",
  energiekilocalories:
    "Un bon apport calorique permet d'apporter suffisamment d'énergie à votre corps, sans excès pouvant contribuer à une prise de poids",
  acidesgrasnocifs:
    "Un apport excessif en acides gras palmitique, myristique et laurique peut favoriser les troubles cardio-vasculaires chez les personnes à risque",
  lipides:
    "Malgré leur mauvaise réputation, les lipides ont un rôle essentiel : dans le stockage de l'énergie, mais aussi dans le fonctionnement normal des cellules",
  sucrestotaux:
    "Un excès de sucres peut avoir des impacts majeurs sur la santé : prise de poids, diabète, problèmes dentaires.",
  proteines:
    "Les protéines peuvent être vues comme de petites briques à partir desquelles le corps renouvelle ses cellules. Elles sont essentielles à tout âge.",
  fibres: "Les fibres jouent un rôle prépondérant au niveau des intestins, pour faciliter le transit.",
  omega6: "",
  omega3_ala: "",
  omega3_dha: "",
  omega3_epa_dha: "",
  sodium:
    "Un excès de sel dans l'organisme augment le risque cardiovasculaire : augmentation de la pression artérielle, développement de maladies. Il peut aussi être reponsable de cas d'ostéoporose, fragilisant les os",
  potassium: "",
  acidesgrassatures:
    "L'impact d'un excès de graisses saturées est sujet à débats au sein de la communauté scientifique. Les AGS ont globablement un effet hypercholestérolémiants, mais les chercheurs sont partagés. L'ANSES recommande néanmoins d'éviter les excès, pouvant augmenter le risque cardio-vasculaire.",
  agmonoinsatures:
    'Considérées comme "les bonnes graisses", les AGMI réduisent le taux de "mauvais cholestérol" (LDL) dans l\'organisme',
  vitaminec:
    "C'est un puissant antioxydant qui joue un rôle dans la stimulation du système immunitaire (lutte contre les infections). Elle intervient dans la synthèse des sels biliaires mais aussi du collagène. Elle est présente dans de très nombreux légumes et fruits mais se dégrade pour partie à la cuisson.",
  vitamineb5:
    "Elle interagit avec les autres vitamines B. Elle joue un rôle essentiel dans l'utilisation des glucides comme des lipides et des protéines consommés. Elle intervient dans la synthèse de certaines hormones. Elle est présente en abondance dans les abats, notamment le foie, mais aussi les champignons, le jaune d'oeuf, les poissons gras, la viande, les légumineuses, le fromage ou encore les céréales complètes, si bien que les carences en cette vitamine sont exceptionnelles.",
  vitamineb12:
    "Elle joue un rôle essentiel dans le renouvellement des tissus et notamment la synthèse des globules rouges et l'utilisation du fer. Avec les vitamines B8 et B9, elle intervient dans la prévention des maladies cardiovasculaires. Elle est présente exclusivement dans les aliments d'origine animale, et en premier lieu dans le foie, les rognons, les coquillages et crustacés. Il n'est donc pas possible de suivre un régime strictement végétalien sans complémentation en vitamine B12.",
  vitaminee:
    "C'est un puissant antioxydant, qui possède également des propriétés anti-inflammatoires. Elle protège des maladies cardiovasculaires et jouerait également un rôle dans le maintien des défenses immunitaires (lutte contre les infections). Elle est essentiellement présente dans les huiles végétales, mais aussi à dose plus faible dans les fruits et légumes et les graisses animales.",
  vitamined:
    "Elle joue un rôle majeur dans le maintien d'une densité osseuse suffisante. Elle est ainsi le complément indispensable au calcium pour avoir des os en bonne santé. Elle jouerait également un rôle dans le maintien des défenses immunitaires (lutte contre les infections). Elle contribue également à la bonne santé de la peau et participerait à la prévention de certains cancers. La vitamine D n'est présente pratiquement que dans des produits animaux : les poissons gras essentiellement, et à faible dose dans certaines viandes, les œufs et les champignons. Mais le corps sait la fabriquer lui-même à partir des rayons du soleil si l'exposition est suffisante : 15 à 30 minutes par jour d'exposition du visage et des bras. Les habitants des régions moins ensoleillées connaissant donc des carences fréquentes.",
  vitaminek:
    "Son rôle essentiel est de permettre la coagulation du sang en cas hémorragie. Les traitements fluidifiants du sang prescrit aux malades cardiaques sont d'ailleurs souvent des « anti-vitamine K ». Elle joue également un rôle dans la fixation du calcium au niveau des os. On la trouve très concentrée dans les légumes à feuilles (salade verte, chou, épinards) et certaines huiles végétales (colza) et à dose plus faible dans de très nombreux aliments animaux comme végétaux.",
  calcium:
    "Le calcium joue un rôle essentiel dans la solidité du squelette. Particulièrement critique en période de croissance, ses apports doivent rester suffisants tout au long de la vie. Le calcium joue aussi un rôle au niveau du système musculaire et du système nerveux.",
  phosphore:
    "Le phosphore est un minéral omniprésent dans notre organisme, en tant que constituant de nos cellules. Il est - avec le calcium - garant de la solidité des os.",
  cuivre:
    "Le cuivre contribue à la formation des globules rouges (système immunitaire), mais également à la minéralisation osseuse et autres fonctions essentielles.",
  fluor: "",
  iode: "L'iode est un acteur essentiel de la gland thiroïdienne. Elle permet notamment la production d'hormones pour la croissance, la maturation cellulaire et le développement du cerveau.",
  vitamineb1:
    "Elle interagit avec les autres vitamines B. Elle joue un rôle essentiel dans l'utilisation de l'énergie issue des glucides consommés et dans la dégradation de l'alcool par le foie. Elle est à l'origine de certains neuromédiateurs utilisés dans l'influx nerveux, et est donc nécessaire à une bonne santé neurologique. On la trouve aussi bien dans les céréales, les fruits à coque (noix), que dans la viande (porc notamment) ou les légumineuses.",
  vitamineb3:
    "Elle ne constitue pas une vitamine au sens strict puisque le corps sait la fabriquer à partir d'acides aminés présents dans les protéines (le tryptophane). Elle intervient avec d'autres vitamines B dans la chaîne respiratoire, mais aussi dans la synthèse de certaines hormones, du cholestérol (qui est indispensable à notre corps, rappelons-le) et de composantes de la bile. Elle entre aussi en jeu dans la mobilisation du calcium et dans la réparation de l'ADN. Elle est présente en abondance dans les viande (notamment le foie), les poissons gras et le thon, mais aussi les céréales complètes...",
  selenium: "Le sélénium ralentit le vieillissement des cellules, et régule notamment les réactions immunitaires",
  betacarotene: "",
  vitamineb2:
    "Elle interagit avec les autres vitamines B. Elle joue un rôle essentiel dans l'utilisation des lipides et protéines consommés. Elle intervient également dans de nombreux mécanismes internes autour de la chaîne respiratoire par exemple. Elle est présente dans de très nombreux aliments animaux comme végétaux : produits laitiers, viandes, poissons, œufs, fruits et légumes, céréales, pommes de terre... si bien que les carences en cette vitamine sont exceptionnelles.",
  vitamineb6:
    "Elle joue un rôle essentiel dans l'utilisation des protéines consommées. Avec les vitamines B9 et B12, elle intervient dans la prévention des maladies cardiovasculaires. Elle est présente dans les céréales complètes, graines et fruits oléagineux, le foie et plus généralement la viande, certains poissons... si bien que les carences en cette vitamine sont exceptionnelles.",
  vitamineb9:
    "Elle intervient dans la synthèse des acides aminés et de l'ADN. Elle agit sur l'immunité et sur l'absorption intestinale. Elle intervient également dans la synthèse des neuromédiateurs. Avec les vitamines B8 et B12, elle intervient dans la prévention des maladies cardiovasculaires. Les aliments les plus riches en acide folique sont le foie, les fruits oléagineux et les châtaignes, puis les légumes verts, légumineuses, œufs et fromages fermentés. Mais elle est présente dans tous les fruits, légumes, viandes, poissons et céréales.",
  vitaminea:
    "Elle est essentielle au bon fonctionnement de la rétine. Elle contribue également à la bonne santé du système immunitaire (lutte contre les infections). Elle participe au renouvellement cellulaire, et donc à la santé de la peau. On la trouve à la fois dans les produits animaux – c'est dans le foie de poisson ou d'animaux d'élevage qu'elle est le plus concentré, mais elle est aussi présente dans le beurre et les produits laitiers gras – et dans les végétaux sous forme de pro-vitamine A (dont le bêta-carotène) fruits et légumes verts ou colorés.",
  magnesium:
    "Le magnésium est un minéral qui permet notamment de réguler le stress nerveux. Il est également un acteur majeur de la digestion, entrant en interaction avec de nombreuses enzymes.",
  fer: "Le fer est un constituant de l'hémoglobline et de la myoglobine, permettant la gestion et distribution de l'oxygène au sein du corps par le biais du sang.",
  zinc: "Le zinc intervient dans de nombreux mécanismes corporels : digestion, hormones, immunité, goût, odorat, peau, cheveux, ...",
};

export const INDICATOR_WHAT_TO_DO = {
  vitamined:
    "80% des français ont une carence en vitamine D. Il est difficile d'atteindre les apports recommandés par seulement l'alimentation. Des compléments alimentaires peuvent supplémenter efficacement. Parlez-en à votre médecin.",
  iode: "Pour éviter les carences en iode, remplacez simplement votre sel par du sel iodé  (disponible dans les commerces). Ceci permet d'atteindre sans difficulté les apports recommandés.",
};

export const CANNOT_BE_DISABLED_INDICATOR = {
  energiekilocalories: "true",
  lipides: "true",
  proteines: "true",
  sucrestotaux: "true",
};
