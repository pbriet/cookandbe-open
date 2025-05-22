
from common.test            import TestAPIWithLogin
from common.date            import tz_aware, make_utc

from mock                   import patch

from emailing               import MessageType

from newsletters.models     import Newsletter

import newsletters.views
import datetime

# class TestSendNewsLetter(TestAPIWithLogin):
    
#     PERMISSIONS = ("author",)
    
#     def setUp(self):
#         super().setUp()
#         Newsletter.objects.create(subject='toto', content='titi', template_name='mandrill1', id=1)
#         Newsletter.objects.create(subject='bar', content='foo', template_name='mandrill2', id=2,
#                                   sent_by=self.user,
#                                   sent_at=datetime.datetime.now())
#         Newsletter.objects.create(subject='eat chocolate', content='now', template_name='mandrill3', id=3)
    
#     def test_newsletter_list(self):
#         response = self.client.get('/secure/api/newsletter/')
#         print(response.data)
#         self.assertEqual(response.status_code, 200)
        
#         # Removing "created_at" unstable data
#         res = response.data
#         for r in res: del r['created_at']
        
#         self.assertEqual(sorted(response.data, key=lambda x: x['id']),
#                          [{'id': 1,
#                            'subject': 'toto'},
#                          {'id': 2,
#                            'subject': 'bar'},
#                          {'id': 3,
#                            'subject': 'eat chocolate'}])
                         
#         response = self.client.get('/secure/api/newsletter/', {'published': False})
#         self.assertEqual(response.status_code, 200)
        
#         # Removing "created_at" unstable data
#         res = response.data
#         for r in res: del r['created_at']
        
#         self.assertEqual(sorted(response.data, key=lambda x: x['id']),
#                          [{'id': 1,
#                            'subject': 'toto'},
#                           {'id': 3,
#                            'subject': 'eat chocolate'}])
    
#     def test_newsletter_remove(self):
#         response = self.client.post('/secure/api/newsletter/1/remove')
#         self.assertEqual(response.status_code, 200)
#         self.assertEqual(sorted([n.id for n in Newsletter.objects.all()]), [2, 3])
        
    
#     def test_newsletter_remove_sent(self):
#         """
#         Cannot remove sent newsletter
#         """
#         response = self.client.post('/secure/api/newsletter/2/remove')
#         self.assertEqual(response.status_code, 200)
#         self.assertEqual(response.data['status'], 'error')
#         self.assertEqual(Newsletter.objects.count(), 3)
        
        
#     @patch('newsletters.views.sendmail')
#     def test_send_phantom_newsletter(self, mock_sendmail):
#         response = self.client.post('/secure/api/newsletter/12/send')
#         self.assertEqual(response.status_code, 400)
#         self.assertEqual(mock_sendmail.call_count, 0)
        
#     @patch('newsletters.views.sendmail')
#     def test_send_already_sent_newsletter(self, mock_sendmail):
#         response = self.client.post('/secure/api/newsletter/2/send')
#         self.assertEqual(response.status_code, 400)
#         self.assertEqual(mock_sendmail.call_count, 0)
        
    
#     @patch('newsletters.views.sendmail')
#     def test_sendnewsletter(self, mock_sendmail):
        
#         user2 = self.create_db_user(roles=['author'])
        
#         response = self.client.post('/secure/api/newsletter/1/send')
#         self.assertEqual(response.status_code, 200)
        
#         self.assertEqual(mock_sendmail.call_count, 1)
#         args, kwargs = mock_sendmail.call_args
#         self.assertEqual(args[0], MessageType.NEWSLETTER)
#         self.assertEqual(args[1], 'toto')
#         self.assertEqual(args[2], 'titi')
#         self.assertEqual([u.email for u in kwargs['users']], ['test@test.fr', 'user_2@test.fr'])
#         self.assertEqual(kwargs['tags'], ['newsletter', 'newsletter_1'])
#         self.assertEqual(kwargs['with_bcc'], False)

#     @patch('newsletters.views.sendmail')
#     def test_send_in_future(self, mock_sendmail):
        
#         response = self.client.post('/secure/api/newsletter/1/send', {'send_at': "2044-08-07T10:46:43.887Z"})
#         self.assertEqual(response.status_code, 200)
        
#         self.assertEqual(mock_sendmail.call_count, 1)
#         args, kwargs = mock_sendmail.call_args
#         expected = make_utc(datetime.datetime(2044, 8, 7, 10, 46, 43))
        
#         self.assertEqual(kwargs['eta'], expected)
#         self.assertEqual(kwargs['expires'], 24*60*60)
