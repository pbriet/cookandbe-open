from common.test                import TestAPIWithLogin
from django.utils               import timezone
import datetime
import json

class TestNotifications(TestAPIWithLogin):
    
    def test_info_notifications(self):
        """
        Test that an information is displayed in notifications.
        And not displayed anymore once it's been read
        """
        self.info = self.create_db_information()
        response = self.client.get('/api/user/%i/notification' % self.user.id)
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['title'], "BREAKING NEWS")
        self.assertEqual(response.data[0]['can_be_read'], True)

        info_id = response.data[0]['id']

        # Mark it as read
        response = self.client.post('/api/user/%i/notification/%i/read' % (self.user.id, info_id))
        self.assertEqual(response.status_code, 201)

        response = self.client.get('/api/user/%i/notification' % self.user.id)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 0)


    def test_old_info_notifications(self):
        """
        Test that an old information is not displayed anymore in notifications.
        """
        valid_until = timezone.now() - datetime.timedelta(days=1)
        self.info = self.create_db_information(valid_until=valid_until)
        response = self.client.get('/api/user/%i/notification' % self.user.id)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 0)

    def _test_expected_notification(self, title, should_be_present=True):
        """
        Test that there is one notification with the given title
        """
        response = self.client.get('/api/user/%i/notification' % self.user.id)
        self.assertEqual(response.status_code, 200)
        for notif in response.data:
            if notif['title'] == title:
                self.assertTrue(should_be_present)
                break
        else:
            self.assertTrue(not should_be_present)

    def test_weight_notifications(self):
        """
        Test that the user is informed about the fact that he needs to
        set his weight
        """
        profile = self.create_db_profile(height=None, weight=None)
        self._test_expected_notification("Poids/Taille non définis")
        profile.height = 40
        profile.weight = 180
        profile.save()
        self._test_expected_notification("Poids/Taille non définis", False)

    def test_tastes_notifications(self):
        """
        Test that the user is informed about the fact that he needs to
        set his tastes
        """
        profile = self.create_db_profile()
        self._test_expected_notification("Goûts non définis")

        food_tag = self.create_db_food_tag()
        taste = self.create_db_taste(food_tag, profile=profile)
        self._test_expected_notification("Goûts non définis", False)

        taste.delete()
        self._test_expected_notification("Goûts non définis")

        self.create_db_restricted_food(food_tag, profile=profile)
        self._test_expected_notification("Goûts non définis", False)

        
        