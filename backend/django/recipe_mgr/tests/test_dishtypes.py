from common.test                import TestAPIWithLogin
from recipe_mgr.models          import DishTypeAggregation

class TestDishTypesAggregation(TestAPIWithLogin):
    def setUp(self):
        TestAPIWithLogin.setUp(self)

        self.dt1 = self.create_db_dishtype()
        self.dt2 = self.create_db_dishtype()
        self.dt3 = self.create_db_dishtype()
        self.master_dt4 = self.create_db_dishtype()
        self.master_dt5 = self.create_db_dishtype()

        # master_dt4 = dt1 + dt2
        DishTypeAggregation.objects.create(master_dish_type=self.master_dt4,
                                              sub_dish_type=self.dt1)
        DishTypeAggregation.objects.create(master_dish_type=self.master_dt4,
                                              sub_dish_type=self.dt2)

        # master_d5 = dt2 + dt3
        DishTypeAggregation.objects.create(master_dish_type=self.master_dt5,
                                              sub_dish_type=self.dt2)
        DishTypeAggregation.objects.create(master_dish_type=self.master_dt5,
                                              sub_dish_type=self.dt3)
        
       
    def test_find_aggregation_api(self):
        # Invalid args
        response = self.client.get('/api/dish_type/find_aggregations', {'dish_type_ids': 'DAMN IT'})
        self.assertEqual(response.status_code, 400)
        response = self.client.get('/api/dish_type/find_aggregations')
        self.assertEqual(response.status_code, 400)
        
        response = self.client.get('/api/dish_type/find_aggregations', {'dish_type_ids': [self.dt1.id]})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, [[self.dt1.id]])

        response = self.client.get('/api/dish_type/find_aggregations', {'dish_type_ids': self.dt1.id})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, [[self.dt1.id]])

        response = self.client.get('/api/dish_type/find_aggregations', {'dish_type_ids': [self.dt1.id, self.dt2.id]})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, [[self.dt1.id, self.dt2.id], [self.master_dt4.id]])

        response = self.client.get('/api/dish_type/find_aggregations', {'dish_type_ids': [self.dt1.id, self.dt2.id, self.dt3.id]})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, [[self.dt1.id, self.dt2.id, self.dt3.id], [self.master_dt4.id, self.dt3.id], [self.dt1.id, self.master_dt5.id]])
        


class TestListDishTypes(TestAPIWithLogin):
    
    def setUp(self):
        TestAPIWithLogin.setUp(self)

        self.dt1 = self.create_db_dishtype()
        self.dt2 = self.create_db_dishtype()
        self.dt3 = self.create_db_dishtype()
        
    def test_list_dish_types(self):
        response = self.client.get('/api/dish_type')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 3)
        
