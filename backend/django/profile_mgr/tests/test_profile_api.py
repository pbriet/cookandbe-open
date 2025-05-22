from common.test                import TestAPIWithLogin
from eater_mgr.models           import Eater
from planning_mgr.models        import MealSlot
from profile_mgr.models         import Profile, User, RecipeDislike
from recipe_mgr.models          import DishType
import json

class TestProfileResource(TestAPIWithLogin):

    def setUp(self):
        super().setUp()
        self.user2 = User.objects.create_user('test2', password='test')
        self.user3 = User.objects.create_user('test3', password='test')

        self.user1_profile1 = self.create_db_profile(creator=self.user)
        self.user1_profile2 = self.create_db_profile(creator=self.user)
        self.user2_profile1 = self.create_db_profile(creator=self.user2)

    def test_get_none(self):
        response = self.client.get('/api/user/%i/profile' % self.user3.id)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, [])

    def test_get_one(self):
        response = self.client.get('/api/user/%i/profile' % self.user2.id)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['id'], self.user2_profile1.id)

    def test_get_two(self):
        response = self.client.get('/api/user/%i/profile' % self.user.id)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 2)
        self.assertEqual(sorted([r['id'] for r in response.data]), [self.user1_profile1.id, self.user1_profile2.id])

class TestCreateProfile(TestAPIWithLogin):
    def setUp(self):
        super().setUp()
        self.init_profile_metrics()

        self.another_user = User.objects.create_user('another', password='test')


    def test_create_profile(self):
        self.init_db_profile_eater()
        # Creating first profile
        response = self.client.post('/api/user/%i/profile' % self.user.id,
                                    {'creator': self.user.id,
                                     'nickname': 'test_prof',
                                     'weight': 70,
                                     'height': 140,
                                     'birth_date': "2001-03-02T00:00:00Z",
                                     'sex': 'male'})
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Profile.objects.filter(creator=self.user).count(), 2)
        profile1 = Profile.objects.get(pk = response.data["id"])
        self.assertEqual(Eater.objects.filter(user=self.user).count(), 2)
        self.assertEqual(profile1.sex, "male")

        # Creating second profile
        response = self.client.post('/api/user/%i/profile' % self.user.id,
                                    {'creator': self.user.id,
                                     'nickname': 'test_prof',
                                     'weight': 50,
                                     'height': 150,
                                     'birth_date': "2002-03-02T00:00:00Z",
                                     'sex': 'female'})
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Profile.objects.filter(creator=self.user).count(), 3)
        profile2 = Profile.objects.get(pk = response.data["id"])
        self.assertFalse(profile2.is_main_profile, "next profiles should be deletable")
        self.assertFalse(self.user.main_profile.id == profile2.id)
        self.assertEqual(Eater.objects.filter(user=self.user).count(), 3)
        self.assertEqual(profile2.sex, "female")

    def test_creating_another_profile_fails(self):
        response = self.client.post('/api/user/%i/profile' % self.user.id,
                                    {'creator': self.another_user.id, # Shouldn't be allowed, because we're logged in with user
                                     'nickname': 'test_prof',
                                     'weight': 70,
                                     'height': 140,
                                     'birth_date': "2001-03-02T00:00:00Z",
                                     'sex': 'male'})
        self.assertEqual(response.status_code, 403)
        self.assertEqual(Profile.objects.filter(creator=self.user).count(), 0)

    def test_creating_another_profile_with_good_user_fails(self):
        response = self.client.post('/api/user/%i/profile' % self.another_user.id, # Inconsistent with creator
                                    {'creator': self.user.id,
                                     'nickname': 'test_prof',
                                     'weight': 70,
                                     'height': 140,
                                     'birth_date': "2001-03-02T00:00:00Z",
                                     'sex': 'male'})
        self.assertEqual(response.status_code, 403)
        self.assertEqual(Profile.objects.filter(creator=self.user).count(), 0)

    def test_creating_profile_with_metaplanning(self):
        # Creating a metaplanning
        self.init_default_meal_type_settings()
        self.init_db_profile_eater()
        metaplanning = self.create_db_meta_planning(with_n_days=1)
        day = metaplanning.days.get()
        # Creating two meal slots, one standard and one custom
        meal_slot1 = self.create_db_mealslot(day)
        meal_slot2 = self.create_db_mealslot(day)
        dish1 = self.create_db_dish(meal_slot1, dish_type=DishType.get_dt(DishType.DT_FULL_COURSE))
        dish2 = self.create_db_dish(meal_slot2, dish_type=DishType.get_dt(DishType.DT_CUSTOM))

        # There shoud be one eater in each meal_slot
        for ms in (meal_slot1, meal_slot2):
            self.assertEqual(ms.eaters.count(), 1)

        # Adding a second profile
        response = self.client.post('/api/user/%i/profile' % self.user.id,
                                    {'creator': self.user.id,
                                     'nickname': 'test_prof',
                                     'weight': 70,
                                     'height': 140,
                                     'birth_date': "2001-03-02T00:00:00Z",
                                     'sex': 'male'})
        print("===================")
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Profile.objects.filter(creator=self.user).count(), 2)
        profile1 = Profile.objects.get(pk = response.data["id"])
        self.assertEqual(Eater.objects.filter(user=self.user).count(), 2)
        self.assertEqual(profile1.sex, "male")

        # There shoud be two eaters in the standard meal_slot
        self.assertEqual(meal_slot1.eaters.count(), 2)
        # And one in the custom one
        self.assertEqual(meal_slot2.eaters.count(), 1)


    def test_create_profile_without_height_weight(self):
        self.init_db_profile_eater()
        response = self.client.post('/api/user/%i/profile' % self.user.id,
                                    {'creator': self.user.id,
                                     'nickname': 'test_prof',
                                     'birth_date': "2001-03-02T00:00:00Z",
                                     'sex': 'male'})
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Profile.objects.filter(creator=self.user).count(), 2)

        data = json.dumps({'creator': self.user.id,
                           'nickname': 'test_prof',
                           'birth_date': "2001-03-02T00:00:00Z",
                           'height': None,
                           'sex': 'male'})
        response = self.client.post('/api/user/%i/profile' % self.user.id, data, content_type="application/json")
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Profile.objects.filter(creator=self.user).count(), 3)

class TestUpdateProfile(TestAPIWithLogin):
    def setUp(self):
        super().setUp()
        self.init_profile_metrics()

        self.another_user = User.objects.create_user('another', password='test')
        self.init_db_profile_eater() # Create main profile and eater

    def test_update_profile(self):
        response = self.client.post('/api/user/%i/profile' % self.user.id,
                                    {'creator': self.user.id,
                                     'nickname': 'test_prof',
                                     'weight': 70,
                                     'height': 140,
                                     'birth_date': "2001-03-02T00:00:00Z",
                                     'sex': 'male'})
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Profile.objects.filter(creator=self.user).count(), 2)
        self.assertEqual(Eater.objects.filter(user=self.user).count(), 2)
        profile = Profile.objects.get(pk = response.data["id"])
        self.assertEqual(profile.sex, "male")
        response = self.client.put('/api/user/%i/profile/%i' % (self.user.id, profile.id),
                                    {'creator': self.user.id,
                                     'nickname': 'test_esseur',
                                     'weight': 42,
                                     'height': 240,
                                     'birth_date': "2000-04-07T00:00:00Z",
                                     'sex': 'female'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Profile.objects.filter(creator=self.user).count(), 2)
        self.assertEqual(Eater.objects.filter(user=self.user).count(), 2)
        profile = Profile.objects.get(pk = response.data["id"])
        self.assertEqual(profile.sex, "female")

class TestDeleteProfile(TestAPIWithLogin):
    def setUp(self):
        super().setUp()
        self.init_profile_metrics()
        self.another_password = "test"
        self.another_login = "another"
        self.another_user = User.objects.create_user(self.another_login, password = self.another_password)

    def test_delete_profile(self):
        # Create main profile
        self.init_db_profile_eater()
        self.assertEqual(Profile.objects.filter(creator=self.user).count(), 1)
        anakin_id = self.profiles[0].id

        # Can't delete main profile
        response = self.client.delete('/api/user/%i/profile/%i' % (self.user.id, anakin_id))
        self.assertEqual(response.status_code, 403)
        self.assertEqual(Profile.objects.filter(creator=self.user).count(), 1)

        # Can delete secondary profile
        response = self.client.post('/api/user/%i/profile' % self.user.id,
                                    {'creator': self.user.id,
                                     'nickname': 'padme',
                                     'weight': 55,
                                     'height': 150,
                                     'birth_date': "1053-03-02T00:00:00Z",
                                     'sex': 'female'})
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Profile.objects.filter(creator=self.user).count(), 2)
        response = self.client.delete('/api/user/%i/profile/%i' % (self.user.id, response.data['id']))
        self.assertEqual(response.status_code, 204)
        self.assertEqual(Profile.objects.filter(creator=self.user).count(), 1)

        # Can't delete someone else's profiles
        response = self.client.post('/api/user/%i/profile' % self.user.id,
                                    {'creator': self.user.id,
                                     'nickname': 'luke',
                                     'weight': 65,
                                     'height': 160,
                                     'birth_date': "1069-03-02T00:00:00Z",
                                     'sex': 'male'})
        self.assertEqual(response.status_code, 201)
        luke_id = response.data['id']
        # Changing current user
        self.assertTrue(self.api_login(login=self.another_login, password=self.another_password))
        self.assertEqual(Profile.objects.filter(creator=self.another_user).count(), 0)
        self.assertEqual(Profile.objects.filter(creator=self.user).count(), 2)
        response = self.client.delete('/api/user/%i/profile/%i' % (self.user.id, anakin_id))
        self.assertEqual(response.status_code, 403) # Should be can't delete main profile status
        response = self.client.delete('/api/user/%i/profile/%i' % (self.user.id, luke_id))
        self.assertEqual(response.status_code, 403) # Should be can't delete other's profile status

class TestDislikeRecipe(TestAPIWithLogin):
    def setUp(self):
        super().setUp()
        self.profile = self.create_db_profile()

        self.recipe1 = self.create_db_recipe()
        self.recipe2 = self.create_db_recipe()

    def _get_disliked_recipe_ids(self):
        res = set()
        for rd in RecipeDislike.objects.all():
            self.assertEqual(rd.profile_id, self.profile.id)
            res.add(rd.recipe_id)
        return res

    def test_recipe_dislike(self):
        for i in range(2):
            response = self.client.post('/api/user/%i/profile/%i/dislike_recipe' % (self.user.id, self.profile.id),
                         json.dumps({'recipe_id': self.recipe1.id}), content_type="application/json")
            self.assertEqual(response.status_code, 200)
            self.assertEqual(self._get_disliked_recipe_ids(), set([self.recipe1.id]))

        response = self.client.post('/api/user/%i/profile/%i/dislike_recipe' % (self.user.id, self.profile.id),
                         json.dumps({'recipe_id': self.recipe2.id}), content_type="application/json")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self._get_disliked_recipe_ids(), set([self.recipe1.id, self.recipe2.id]))
