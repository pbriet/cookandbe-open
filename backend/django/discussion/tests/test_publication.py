
from discussion.models              import Discussion, Publication, Message
from discussion.serializers         import DiscussionSerializer, PublicationSerializer
from discussion.tests               import BaseTestDiscussion

from common.test                    import TestAPIWithLogin, OptalimTest, add_permissions
from common.mock_tools              import FakeNow

from mock                           import patch, MagicMock, call

import datetime

class TestPublication(BaseTestDiscussion):
    def setUp(self):
        super().setUp()
        self.dietician  = self.create_db_user(name = "Test Dukan", roles = ("dietician", ), auto_create_main_profile = True)
        self.liberty    = self.create_db_user(name = "Liberty subscriber", subscription_level = 1, auto_create_main_profile = True)
        self.premium    = self.create_db_user(name = "Premium subscriber", subscription_level = 2, auto_create_main_profile = True)
        self.god        = self.create_db_user(name = "42", roles = ("admin", ))
        self.assertEqual(self.user.subscription_level, 0)

    def test_public_access(self):
        publication = self.create_db_publication(self.thierry, public = True)
        expected = (
            (None,          200), # anonymous
            (self.thierry,  200), # dietician
            (self.dietician,200), # other dietician
            (self.user,     200), # free user
            (self.liberty,  200), # liberty user
            (self.premium,  200), # premium user
            (self.god,      200), # admin
        )
        for user, expected_code in expected:
            data = self.api_get_publication(publication, user, expected_code = expected_code)
            if user is None:
                self.assertTrue("response" not in data)

    def test_internal_access(self):
        publication = self.create_db_publication(self.thierry, public = False)
        expected = (
            (None,          404), # anonymous
            (self.thierry,  200), # dietician
            (self.dietician,200), # other dietician
            (self.user,     404), # free user
            (self.liberty,  404), # liberty user
            (self.premium,  404), # premium user
            (self.god,      200), # admin
        )
        for user, expected_code in expected:
            print(user and user.first_name)
            data = self.api_get_publication(publication, user, expected_code = expected_code)

    def test_creation(self):
        expected = (
            (None,          401), # anonymous
            (self.thierry,  201), # dietician
            (self.dietician,201), # other dietician
            (self.user,     403), # free user
            (self.liberty,  403), # liberty user
            (self.premium,  403), # premium user
            (self.god,      201), # admin
        )
        for user, expected_code in expected:
            self.api_create_publication(user, expected_code)

    def test_modification(self):
        publication = self.create_db_publication(self.thierry, public = True, user_sex = True)
        expected = (
            (None,          401), # anonymous
            (self.thierry,  200), # dietician
            (self.dietician,200), # other dietician
            (self.user,     403), # free user
            (self.liberty,  403), # liberty user
            (self.premium,  403), # premium user
            (self.god,      200), # admin
        )
        for user, expected_code in expected:
            self.api_change_publication(publication, user, self.get_publication_args(self.thierry, user_sex = False), expected_code = expected_code)

    def test_list(self):
        # Results should be filtered and reverse time sorted
        with FakeNow(*self.get_next_now()):
            p4 = self.create_db_publication(self.god, public = False)
        with FakeNow(*self.get_next_now()):
            p3 = self.create_db_publication(self.thierry, public = True)
        with FakeNow(*self.get_next_now()):
            p2 = self.create_db_publication(self.thierry, public = False)
        with FakeNow(*self.get_next_now()):
            p1 = self.create_db_publication(self.god, public = True)
        expected = (
            (None,          200, (p1, p3)),         # anonymous
            (self.thierry,  200, (p1, p2, p3, p4)), # dietician
            (self.dietician,200, (p1, p2, p3, p4)), # other dietician
            (self.user,     200, (p1, p3)),         # free user
            (self.liberty,  200, (p1, p3)),         # liberty user
            (self.premium,  200, (p1, p3)),         # premium user
            (self.god,      200, (p1, p2, p3, p4)), # admin
        )
        for user, expected_code, expected_items in expected:
            publications = self.api_list_publications(user, expected_code = expected_code)
            self.assertEqual(len(publications), len(expected_items))
            for publication, item in zip(publications, expected_items):
                for key, value in publication.items():
                    print("attribute", key)
                    self.assertEqual(PublicationSerializer(item).data[key], value)

    def test_search(self):
        with FakeNow(*self.get_next_now()):
            p4 = self.create_db_publication(self.god, question = 'Comment je peux grossir ?', public = False)
        with FakeNow(*self.get_next_now()):
            p3 = self.create_db_publication(self.thierry, question = 'Comment je peux grossir ?', public = True)
        with FakeNow(*self.get_next_now()):
            p2 = self.create_db_publication(self.thierry, question = 'Comment je peux mincir ?', public = False)
        with FakeNow(*self.get_next_now()):
            p1 = self.create_db_publication(self.god, question = 'Comment je peux mincir ?', public = True)
        expected = (
            # Hidden == False & no keywords
            (None,          "", False, (p1, p3)),
            (self.thierry,  "", False, (p1, p2, p3, p4)),
            (self.dietician,"", False, (p1, p2, p3, p4)),
            (self.user,     "", False, (p1, p3)),
            (self.liberty,  "", False, (p1, p3)),
            (self.premium,  "", False, (p1, p3)),
            (self.god,      "", False, (p1, p2, p3, p4)),
            # Hidden == True & no keywords
            (None,          "", True,  (p1, p3)),
            (self.thierry,  "", True,  (p2, p4)),
            (self.dietician,"", True,  (p2, p4)),
            (self.user,     "", True,  (p1, p3)),
            (self.liberty,  "", True,  (p1, p3)),
            (self.premium,  "", True,  (p1, p3)),
            (self.god,      "", True,  (p2, p4)),
            # Hidden == False & Keywords == MinCIR pEuX
            (None,          "MinCIR   pEuX", False,  (p1, )),
            (self.thierry,  "MinCIR   pEuX", False,  (p1, p2)),
            (self.dietician,"MinCIR   pEuX", False,  (p1, p2)),
            (self.user,     "MinCIR   pEuX", False,  (p1, )),
            (self.liberty,  "MinCIR   pEuX", False,  (p1, )),
            (self.premium,  "MinCIR   pEuX", False,  (p1, )),
            (self.god,      "MinCIR   pEuX", False,  (p1, p2)),
            # Hidden == True & Keywords == MinCIR pEuX
            (None,          "MinCIR   pEuX", True,  (p1, )),
            (self.thierry,  "MinCIR   pEuX", True,  (p2, )),
            (self.dietician,"MinCIR   pEuX", True,  (p2, )),
            (self.user,     "MinCIR   pEuX", True,  (p1, )),
            (self.liberty,  "MinCIR   pEuX", True,  (p1, )),
            (self.premium,  "MinCIR   pEuX", True,  (p1, )),
            (self.god,      "MinCIR   pEuX", True,  (p2, )),
        )
        for user, keywords, hidden, expected_items in expected:
            search = self.api_search_publications(user, keywords, hidden, expected_code = 200)
            print(user and user.first_name, keywords, hidden)
            self.assertEqual(search['count'], len(expected_items))
            for publication, item in zip(search['results'], expected_items):
                for key, value in publication.items():
                    self.assertEqual(PublicationSerializer(item).data[key], value)