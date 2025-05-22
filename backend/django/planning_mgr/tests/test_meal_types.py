from common.test                import TestAPIWithLogin

class TestMealTypes(TestAPIWithLogin):

    def setUp(self):
        super().setUp()

        self.dt1 = self.create_db_dishtype("first one")
        self.dt2 = self.create_db_dishtype("second one")
        
        self.agg_dt, self.sub_dt1, self.sub_dt2 = self.create_db_dishtype_aggregated()

        self.meal_type = self.create_db_mealtype(dish_types=[self.dt2, self.sub_dt1, self.sub_dt2])

    def test_mealtype_dishtypes(self):
        response = self.client.get("/api/dish_type/from_meal_type/%i" % self.meal_type.id)
        print(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, {"dish_types": [
                                                {"id": self.dt2.id, "name": "second one"},
                                                {"id": self.sub_dt1.id, "name": "main"},
                                                {"id": self.sub_dt2.id, "name": "side"},
                                                {"id": self.agg_dt.id, "name": "full meal"},
                                                ]
                                                })