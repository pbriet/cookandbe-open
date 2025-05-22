from shopping_mgr.tests         import TestBaseShoppingListTest
from shopping_mgr.models        import ShoppingItem
from mock                       import patch
import re

class TestShoppingListGeneration(TestBaseShoppingListTest):

    WITH_FOOD_TYPES = None

    def _check_mail_content(self, mock_email_message, must_have_strs, must_not_have_strs=None):
        """
        Checks that email has been sent and what is its content
        """
        self.assertTrue(mock_email_message.called)

        args, kwargs = mock_email_message.call_args
        self.assertEqual(args[1], "Votre liste de courses")
        cleaned_message = args[2].replace('\n', ' ').replace('\r', '')
        cleaned_message = re.sub(' +', ' ', cleaned_message)
        for str_value in must_have_strs:
            if str_value not in cleaned_message:
                print("can't find %s in email content" % str_value)
            self.assertTrue(str_value in cleaned_message)
        if must_not_have_strs:
            for str_value in must_not_have_strs:
                self.assertTrue(str_value not in cleaned_message)
        self.assertEqual(len(kwargs['users']), 1)
        self.assertEqual(kwargs['users'][0].email, "test@test.fr")
        self.assertEqual(kwargs['tags'], ['shopping_list'])
        self.assertEqual(kwargs['eta'], None)
        self.assertEqual(kwargs['send_async'], False)
        self.assertEqual(kwargs['expires'], None)


    def _call_api_sendmail(self):
        response = self.client.post('/api/user/%i/shopping_list/%i/send_by_mail' % (self.user.id, self.shopping_list.id))
        self.assertEqual(response.status_code, 200)


    @patch('emailing.tools.sendmail')
    def test_basic(self, mock_email_message):

        self._call_api_sendmail()
        self._check_mail_content(mock_email_message,
                                 ["carrots", "9 small", "chocolate", "7 chunks", "Mardi 8 à Vendredi 11"])

    @patch('emailing.tools.sendmail')
    def test_shopping_list_with_missing(self, mock_email_message):

        # Checking carrots
        ShoppingItem.objects.filter(food_id=self.carrots.id).update(got_it=True)

        self._call_api_sendmail()
        self._check_mail_content(mock_email_message,
                                 ["chocolate", "7 chunks", "Mardi 8 à Vendredi 11"],
                                 ["carrots", "9 small"])
