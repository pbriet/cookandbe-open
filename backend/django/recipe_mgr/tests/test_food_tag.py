from common.test                    import TestAPIWithLogin, add_permissions, pgsql_only
from recipe_mgr.models              import FoodTagSet
from optalim.config                 import Config
import json

class TestFoodTagApi(TestAPIWithLogin):
    def setUp(self):
        super().setUp()
        self.darkChocolate  = self.create_db_food("dark chocolate")
        self.milk           = self.create_db_food("milk bottle")
        self.milkChocolate  = self.create_db_food("milk chocolate")
        self.candy          = self.create_db_food("candy")
        self.chocolateTag   = self.create_db_food_tag(name = "chocolate")
        self.milkTag        = self.create_db_food_tag(name = "milk")
        self.junkFoodTag    = {'id': None, 'name': 'Junk food'}

    def _getJson(self, databaseObject, with_id = True, defaultDict = None):
        id_suffix = '_id'
        res = defaultDict or dict()
        for key, value in databaseObject.__dict__.items():
            if key[0] == '_':
                continue
            if key.endswith(id_suffix) and not with_id:
                res[key[:-len(id_suffix)]] = value
            else:
                res[key] = value
        return res

    @add_permissions("admin")
    def test_food_tag_set(self):
        # Post without nested
        response = self.client.post('/secure/api/food_tag_set', {'tag': self.chocolateTag.id, 'food': self.darkChocolate.id})
        self.assertEqual(response.status_code, 201)
        del response.data['id']
        self.assertEqual(response.data, {'food': self.darkChocolate.id, 'tag': self.chocolateTag.id, 'component': False})
        
        # Get without filter
        response = self.client.get('/secure/api/food_tag_set')
        self.assertEqual(response.status_code, 200)
        del response.data[0]['id']
        self.assertEqual(response.data, [{
            'tag': self.chocolateTag.id,
            'component': False,
            'food': {
                'id': self.darkChocolate.id,
                'parent': None,
                'food_source': None,
                'fresh_expiry': None,
                'enabled': True,
                'type': self.food_type.id,
                'original': None,
                'tags': [self.chocolateTag.id],
                'name': 'dark chocolate',
                'full_name': 'dark chocolate',
                'has_nutrients': True,
                'default_conversion': None,
                'default_raw_state': None,
                'default_cooking_method': None,
                'shopping_category': self.default_shopping_category.id
            }
        }])
            
        # Get with filter
        response = self.client.get('/secure/api/food_tag_set', {'food_id': self.milkChocolate.id})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, [])
        
        
        # Post with nested object
        response = self.client.post('/secure/api/food_tag_set',
                                    json.dumps({'tag': self.chocolateTag.id, 'food': self._getJson(self.milkChocolate)}),
                                    content_type="application/json")
        self.assertEqual(response.status_code, 201)
        del response.data['id']
        self.assertEqual(response.data, {'food': self.milkChocolate.id, 'tag': self.chocolateTag.id, 'component': False})
        # Get with filter and nested
        response = self.client.get('/secure/api/food_tag_set', {'tag_id': self.chocolateTag.id, 'nested': 'food'})
        self.assertEqual(response.status_code, 200)
        del response.data[0]['id']
        del response.data[1]['id']
        self.assertEqual(response.data, [{'food': self._getJson(self.darkChocolate, with_id = False, defaultDict = {'tags' : [self.chocolateTag.id]}),
                                          'tag': self.chocolateTag.id, 'component': False},
                                         {'food': self._getJson(self.milkChocolate, with_id = False, defaultDict = {'tags' : [self.chocolateTag.id]}),
                                          'tag': self.chocolateTag.id, 'component': False}
                                        ])
       
        # Get with filter resulting empty
        response = self.client.get('/secure/api/food_tag_set', {'tag_id': self.chocolateTag.id + 100})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 0)
        
        ### ERRORS ###
        
        # Get with invalid nested
        response = self.client.get('/secure/api/food_tag_set', {'nested': 'toto'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 2)
        # Get with invalid filter
        response = self.client.get('/secure/api/food_tag_set', {'plop_id': 3})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 2)
        # Post with invalid nested
        d = self._getJson(self.candy, with_id=False)
        d['food_source'] = {'id' : 1}
        d['nested'] = 'food_source'
        response = self.client.post('/secure/api/food',
                                    json.dumps(d),
                                    content_type="application/json")
        self.assertEqual(response.status_code, 400)

    @add_permissions("admin")
    def test_filter_food_tags_by_food(self):
        """
        Test filtering food tags with a food
        """
        # 2 foos tagged for chocolate, 1 for milk
        FoodTagSet.objects.create(tag = self.chocolateTag, food = self.darkChocolate)
        FoodTagSet.objects.create(tag = self.chocolateTag, food = self.milkChocolate)
        FoodTagSet.objects.create(tag = self.milkTag, food = self.milkChocolate)
        self.otherFoodTag        = self.create_db_food_tag(name = "another_foodtag")
        FoodTagSet.objects.create(tag = self.otherFoodTag, food = self.candy)

        response = self.client.get('/api/food_tag', {'food_id': self.milkChocolate.id})
        print(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 2)
        self.assertEqual(response.data[0]['id'], self.milkTag.id)
        self.assertEqual(response.data[1]['id'], self.chocolateTag.id)
        
    def test_food_tag_from_key(self):
        url_key = self.chocolateTag.url_key
        response = self.client.get('/api/food_tag/from_key/%s' % url_key)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['id'], self.chocolateTag.id)

class BaseTestFoodTagSearch(TestAPIWithLogin):
    def setUp(self):
        super().setUp()
        self.food = self.create_db_food()
        for tag_name in ("chocolate", "whiteeee chocolate", "ploppy chocolat", "milk", "milky chocolate", "carrot"):
            self.create_db_food_tag(name = tag_name, foods=[self.food])
    
    def _test_search(self, query, expected, status = 200, params = {}):
        response = self.client.get('/api/food_tag/search/' + query, params)
        self.assertEqual(response.status_code, status)
        if status == 200:
            res = [food_tag['name'] for food_tag in response.data['food_tags']]
            print(res)
            self.assertEqual(res, expected)

class TestFoodTagSearch(BaseTestFoodTagSearch):
    
    def test_search(self):
        self._test_search('chocolate', ['chocolate', 'milky chocolate', 'whiteeee chocolate'])
        self._test_search('milk',  ['milk', 'milky chocolate'])
        self._test_search('milky',  ['milky chocolate'])

class TestFoodTagSearchDislikable(BaseTestFoodTagSearch):
    
    def setUp(self):
        super().setUp()
        children = []
        for tag_name in ("E0042", "E00666", "Edulcorants"):
            children.append(self.create_db_food_tag(name = tag_name, foods = [self.food], can_be_disliked = False, children = None if tag_name != "Edulcorants" else children))
    
    def test_search_user(self):
        self._test_search('E00', [], params = {"allow_non_dislikables": False})
        self._test_search('edul',  [], params = {"allow_non_dislikables": False})
        self._test_search('E00', [], status = 403, params = {"allow_non_dislikables": True})
        self._test_search('edul', [], status = 403, params = {"allow_non_dislikables": True})
        
    @add_permissions("admin")
    def test_search_admin(self):
        self._test_search('E00', [], params = {"allow_non_dislikables": False})
        self._test_search('edul',  [], params = {"allow_non_dislikables": False})
        self._test_search('E00', ['E0042', 'E00666'], params = {"allow_non_dislikables": True})
        self._test_search('edul',  ['Edulcorants'], params = {"allow_non_dislikables": True})
        
    @add_permissions("operator")
    def test_search_operator(self):
        self._test_search('E00', [], params = {"allow_non_dislikables": False})
        self._test_search('edul',  [], params = {"allow_non_dislikables": False})
        self._test_search('E00', ['E0042', 'E00666'], params = {"allow_non_dislikables": True})
        self._test_search('edul',  ['Edulcorants'], params = {"allow_non_dislikables": True})

class TestFoodTagSearchAccents(BaseTestFoodTagSearch):
    def setUp(self):
        super().setUp()
        for tag_name in ("milké", "milkee", "milkàaa"):
            self.create_db_food_tag(name = tag_name, foods=[self.food])
            
    @pgsql_only
    def test_search_with_accents(self):
        self._test_search('milk',  ['milk', "milké", "milkee", "milkàaa", 'milky chocolate'])
        self._test_search('milke',  ["milké", "milkee"])
        self._test_search('milké',  ["milké", "milkee"])
        self._test_search('milkée',  ["milkee"])
        self._test_search('milkaàà',  ["milkàaa"])

class BaseTestFoodTagHierarchy(TestAPIWithLogin):
    def setUp(self):
        super().setUp()
        self.tag1 = self.create_db_food_tag("tag1")
        self.tag2 = self.create_db_food_tag("tag2")
        self.tag3 = self.create_db_food_tag("tag3")
        self.tag4 = self.create_db_food_tag("tag4")
        self.tag5 = self.create_db_food_tag("tag5")
        # Tag1 is the parent of tag2 and tag3
        self.tag1.children.add(self.tag2)
        self.tag1.children.add(self.tag3)

class TestFoodTagHierarchy(BaseTestFoodTagHierarchy):
    
    def test_get_children(self):
        response = self.client.get('/api/food_tag/%i/children' % self.tag1.id)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(sorted([r['name'] for r in response.data]), ['tag2', 'tag3'])
        
    def test_get_parents(self):
        response = self.client.get('/api/food_tag/%i/parents' % self.tag2.id)
        self.assertEqual(response.status_code, 200)
        self.assertEqual([r['name'] for r in response.data], ['tag1'])
    
    def _check_tag1_children(self, expected):
        tag1_children = [t.name for t in self.tag1.children.all()]
        self.assertEqual(sorted(tag1_children), expected)
        
    @add_permissions("admin")
    def test_add_child(self):
        response = self.client.post('/secure/api/food_tag/%i/add_child' % self.tag1.id, {'food_tag_id': self.tag4.id})
        self.assertEqual(response.status_code, 200)
        
        self._check_tag1_children(["tag2", "tag3", "tag4"])
        
        response = self.client.post('/secure/api/food_tag/%i/add_child' % self.tag1.id, {'food_tag_id': self.tag4.id})
        self.assertEqual(response.status_code, 400)
        self._check_tag1_children(["tag2", "tag3", "tag4"])
        
    @add_permissions("admin")
    def test_remove_child(self):
        response = self.client.post('/secure/api/food_tag/%i/remove_child' % self.tag1.id, {'food_tag_id': self.tag2.id})
        self.assertEqual(response.status_code, 200)
        
        self._check_tag1_children(["tag3"])
        
        response = self.client.post('/secure/api/food_tag/%i/remove_child' % self.tag1.id, {'food_tag_id': self.tag2.id})
        self.assertEqual(response.status_code, 400)
        self._check_tag1_children(["tag3"])

class TestSearchRecipesByFoodTag(BaseTestFoodTagHierarchy):
    
    def setUp(self):
        super().setUp()
        self.init_default_ingredient_settings()
        self.recipe1 = self.create_db_recipe("recipe1")
        self.recipe2 = self.create_db_recipe("recipe2")
        self.recipe3 = self.create_db_recipe("recipe3")
        
        self.food1 = self.create_db_food("food1")
        self.create_db_ingredient(self.recipe1, self.food1)
        self.food2 = self.create_db_food("food2")
        self.create_db_ingredient(self.recipe2, self.food2)
        self.food3 = self.create_db_food("food3")
        self.create_db_ingredient(self.recipe3, self.food3)
        
        # Food1 is tagged tag2, which is a child of tag1
        self.db_assign_food_to_foodtag(self.food1, self.tag2)
        
        # Food2 is tagged tag1
        self.db_assign_food_to_foodtag(self.food2, self.tag1)
        
        # Food3 is tagged tag4
        self.db_assign_food_to_foodtag(self.food3, self.tag4)
    
    def _test_search(self, food_tag_id, expected_results):
        response = self.client.get('/api/recipe/from_food_tag/%i' % food_tag_id)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['count'], len(expected_results))
        recipes = []
        for recipe in response.data['results']:
            recipes.append(recipe['name'])
        self.assertEqual(sorted(recipes), expected_results)
        
    def test_search_food_tag_with_hierarchy(self):
        self._test_search(self.tag1.id, ['recipe1', 'recipe2'])
        
    def test_search_food_tag_simple(self):
        self._test_search(self.tag4.id, ['recipe3'])
        
    def test_search_food_tag_empty(self):
        self._test_search(self.tag5.id, [])

class TestFoodTagAnomalies(TestAPIWithLogin):
    
    def setUp(self):
        super().setUp()
        
        self.food1 = self.create_db_food("food1")
        self.food2 = self.create_db_food("food2")
        self.food3 = self.create_db_food("food3")
        
        # Tag1 contains all the foods, Tag2 contains food1 and food2 only
        self.tag1 = self.create_db_food_tag("tag1", foods=[self.food1, self.food2, self.food3])
        self.tag2 = self.create_db_food_tag("tag2", foods=[self.food1, self.food2])
        self.tag3 = self.create_db_food_tag("tag3")
        
    def test_find_anomalies_on_empty(self):
        
        response = self.client.get('/api/food_tag/%i/find_anomalies' % self.tag3.id)
        self.assertEqual(response.status_code, 200)
        
        suggested = response.data["suggested_modifications"]
        self.assertEqual(len(suggested), 0)
        
    def test_find_anomalies(self):
        """
        Test the detection of potential anomalies in the food tag content :
        foods that should be replaced by some food tags
        """
        
        # Tag2 should be replacing food1 and food2 within Tag1
        response = self.client.get('/api/food_tag/%i/find_anomalies' % self.tag1.id)
        self.assertEqual(response.status_code, 200)
        
        suggested = response.data["suggested_modifications"]
        self.assertEqual(len(suggested), 1)
        
        suggested = suggested[0]
        self.assertEqual(suggested["food_tag"]["id"], self.tag2.id)
        
        self.assertEqual(sorted(f['name'] for f in suggested["foods"]), ["food1", "food2"])
        
        # No anomaly when it's done
        self.tag1.delete()
        self.tag1 = self.create_db_food_tag("tag1", foods=[self.food3])
        self.tag1.children.add(self.tag2)
        
        response = self.client.get('/api/food_tag/%i/find_anomalies' % self.tag1.id)
        self.assertEqual(response.status_code, 200)
        
        suggested = response.data["suggested_modifications"]
        self.assertEqual(len(suggested), 0)
        