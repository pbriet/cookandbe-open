PROJECT DJANGO
-----------------

* **eater_mgr** est l'application de gestion des compagnons de repas (amis, famille)

* **frontend** est l'application qui gère l'affichage du site en frontend (NOTE: cette partie est amenée à disparaitre au profit
  d'AngularJS en mode complètement autonome.)

* **hippocrate** ensemble des sources de l'algorithme de génération de plannings

* **optalim** contient les fichiers principaux du projet (settings, urls, ...)

* **planning_mgr** est l'application de gestion des plannings de repas

* **profile_mgr** est l'application de gestion des profils utilisateurs (goûts, condition médicale)

* **provider_mgr** est l'application de gestion des fournisseurs de nourriture (grande surface, producteurs locaux, potager)

* **recipe_mgr** est l'application de gestion des recettes (édition et visualisation via une API REST)

* **shopping_mgr** est l'application de gestion des listes de course

* **storage_mgr** est l'application de gestion des stocks de nourriture (réfrigirateur, placards)

* **user_mgr** est l'application de gestion des utilisateurs


Gérer les migrations du modèle
------------------------------

Après une modification du modèle, voici la marche à suivre:

* Créer la migration avec south: `./manage.py schemamigration <app_name> --auto`

* Si besoin, éditer le fichier généré par South

* Appliquer la migration: `./manage.py migrate <app_name>`

* Si des fixtures existantes utilisent ce modèle, les mettre à jour avec: `/deployment/tools/migrate_fixtures.sh`



Tests : créer une fixture
-------------------------

Il existe une commande afin d'extraire des recettes et ses données associées afin d'en faire une fixture

`./manage.py dumprecipe <recipe_id> <recipe_id>`

Les options suivantes sont disponibles :

* `--nutrients`: dumpe les données relatives aux nutriments pour ces recettes (par défaut: non)

* `--nutrient-ids=<nutrient_id>,<nutrient_id> ...`: ne dumpe que certains nutriments.


