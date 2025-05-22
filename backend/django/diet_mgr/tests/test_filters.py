from common.test                        import TestAPIWithLogin, add_permissions


class DietFilters(TestAPIWithLogin):
    """
    Testing the edition of diet food tags through API,
    and generation of hippocrate filters
    """
    def setUp(self):
        super().setUp()
        
        self.profile = self.create_db_profile()
        
        self.food_tags = {}
        
        for food_tag_name in ('plip', 'plop', 'plup', 'plaf', 'booh'):
            self.food_tags[food_tag_name] = self.create_db_food_tag(food_tag_name)
            
        for excluded_name in ('plip', 'plup', 'booh'):
            self.diet.excluded_food_tags.add(self.food_tags[excluded_name])


    def test_filters(self):
        handler = self.diet.handler(self.profile)
        
        filters = list(handler.filters())
        self.assertEqual(len(filters), 3)
        
        food_tag_ids = [f.food_tag_id for f in filters]
        expected = [self.food_tags[name].id for name in ('plip', 'plup', 'booh')]
        self.assertEqual(sorted(food_tag_ids), sorted(expected))
        
        
    def _assert_excluded_from_api(self, expected):
        response = self.client.get('/api/diet/%i/excluded_foodtags' % self.diet.id)
        self.assertEqual(response.status_code, 200)
        f_names = []
        for food_tag in response.data:
            f_names.append(food_tag['name'])
        
        self.assertEqual(sorted(f_names), expected)
    
    @add_permissions("operator")
    def test_add_food_tags(self):
        # Initial list of food tags
        self._assert_excluded_from_api(['booh', 'plip', 'plup'])
        
        # Excluding a new food tag
        response = self.client.post('/secure/api/diet/%i/exclude_foodtag' % self.diet.id,
                                    {'food_tag_id': self.food_tags['plaf'].id})
        self.assertEqual(response.status_code, 201)
        
        self._assert_excluded_from_api(['booh', 'plaf', 'plip', 'plup'])
        
        # Excluding a food tag that is already excluded
        response = self.client.post('/secure/api/diet/%i/exclude_foodtag' % self.diet.id,
                                    {'food_tag_id': self.food_tags['booh'].id})
        self.assertEqual(response.status_code, 400)
        
        self._assert_excluded_from_api(['booh', 'plaf', 'plip', 'plup'])
    
    @add_permissions("operator")
    def test_undo_add_food_tags(self):
        # Un-excluding a food tag
        response = self.client.post('/secure/api/diet/%i/undo_exclude_foodtag' % self.diet.id,
                                    {'food_tag_id': self.food_tags['plip'].id})
        self.assertEqual(response.status_code, 201)
        self._assert_excluded_from_api(['booh', 'plup'])
        
        # Un-excluding a food tag that is not excluded
        response = self.client.post('/secure/api/diet/%i/undo_exclude_foodtag' % self.diet.id,
                                    {'food_tag_id': self.food_tags['plaf'].id})
        self.assertEqual(response.status_code, 400)
        self._assert_excluded_from_api(['booh', 'plup'])