
from django.core.exceptions import ValidationError

from common.decorators      import api_arg, api_model_arg
from common.test            import OptalimTest

from profile_mgr.models     import Profile

from mock                   import Mock
import datetime

fake_request = Mock(data={}, GET={})
fake_viewset = Mock(request=fake_request)

class TestArgDecorators(OptalimTest):

    def test_api_arg_int(self):

        @api_arg('my_int', int)
        def my_api_fcn(request, my_int):
            return my_int

        self.assertEqual(my_api_fcn(fake_viewset, my_int="35"), 35)
        
        res = my_api_fcn(fake_viewset, my_int="3a")
        self.assertEqual(res.status_code, 400)

        res = my_api_fcn(fake_viewset)
        self.assertEqual(res.status_code, 400)


        @api_arg('my_int', int, 12)
        def my_api_fcn(request, my_int):
            return my_int

        self.assertEqual(my_api_fcn(fake_viewset, my_int="22"), 22)
        self.assertEqual(my_api_fcn(fake_viewset), 12)

    def test_api_arg_date(self):

        @api_arg('my_date', datetime.date)
        def my_api_fcn(request, my_date):
            return my_date

        self.assertEqual(my_api_fcn(fake_viewset, my_date="2011-05-06"), datetime.date(2011, 5, 6))

        res = my_api_fcn(fake_viewset, my_date="201-05-06")
        self.assertEqual(res.status_code, 400)

        def before_2000(value):
            if value.year >= 2000:
                raise ValidationError("Year should be lower than 2000")

        @api_arg('my_date', datetime.date, validators=[before_2000])
        def my_api_fcn(request, my_date):
            return my_date

        res = my_api_fcn(fake_viewset, my_date="2011-05-06")
        self.assertEqual(res.status_code, 400)

        res = my_api_fcn(fake_viewset, my_date="1999-05-06")
        self.assertEqual(res, datetime.date(1999, 5, 6))
    
    def test_api_arg_list(self):

        @api_arg('my_int_list', int, is_list=True)
        def my_api_fcn(request, my_int_list):
            return my_int_list

        self.assertEqual(my_api_fcn(fake_viewset, my_int_list=["34", "35"]), [34, 35])

        res = my_api_fcn(fake_viewset, my_int_list="33")
        self.assertEqual(res.status_code, 400)

class TestModelArgDecorators(OptalimTest):

    def setUp(self):
        super().setUp()
        self.create_db_profile()

    def test_api_model_arg(self):
        @api_model_arg('profile', Profile)
        def my_api_fcn(request, profile):
            return profile

        # Standard
        self.assertEqual(my_api_fcn(fake_viewset, profile_id = self.user.main_profile.id), self.user.main_profile)
        
        # Invalid id
        res = my_api_fcn(fake_viewset, profile_id = self.user.main_profile.id + 1)
        self.assertEqual(res.status_code, 400)

        # Missing id
        res = my_api_fcn(fake_viewset)
        self.assertEqual(res.status_code, 400)

        # Allow none
        @api_model_arg('profile', Profile, allow_none = True)
        def my_api_fcn(request, profile):
            return profile

        self.assertEqual(my_api_fcn(fake_viewset, profile_id = self.user.main_profile.id), self.user.main_profile)
        self.assertEqual(my_api_fcn(fake_viewset), None)
        
        # Non standard id
        @api_model_arg('profile', Profile, id_arg_name = "pk")
        def my_api_fcn(request, profile):
            return profile

        self.assertEqual(my_api_fcn(fake_viewset, pk = self.user.main_profile.id), self.user.main_profile)

    def test_api_model_arg_list(self):
        # Mono-list
        @api_model_arg('profiles', Profile, is_list = True, id_arg_name = "my_profile_ids")
        def my_api_fcn(request, profiles):
            return list(profiles)

        self.assertEqual(my_api_fcn(fake_viewset, my_profile_ids = [self.user.main_profile.id, ]), [self.user.main_profile, ])

        # Creating 2nd profile
        profile2 = self.create_db_profile()

        self.assertEqual(my_api_fcn(fake_viewset, my_profile_ids = [self.user.main_profile.id, profile2.id]), [self.user.main_profile, profile2])

        # Standard id_name
        @api_model_arg('profiles', Profile, is_list = True)
        def my_api_fcn(request, profiles):
            return list(profiles)

        self.assertEqual(my_api_fcn(fake_viewset, profile_ids = [profile2.id, ]), [profile2, ])

        # Bad list
        res = my_api_fcn(fake_viewset, profile_ids = profile2.id)
        self.assertEqual(res.status_code, 400)
