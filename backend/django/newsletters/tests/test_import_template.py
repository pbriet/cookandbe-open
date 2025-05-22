
from common.test            import TestAPIWithLogin

from mock                   import patch

from newsletters.models     import Newsletter

import newsletters.views
import datetime

FAKE_TEMPLATES = [{'updated_at': '2012-03-05 15:21:33.47326',
                   'name': 'template1'},
                  {'updated_at': '2014-01-02 06:10:02.47326',
                   'name': 'the_template2'}]

class FakeMandrill(object):
    def __init__(self, *args, **kargs):
        pass
    
    @property
    def templates(self):
        class Obj(object):
            @staticmethod
            def list():
                return FAKE_TEMPLATES
            @staticmethod
            def info(name=None):
                if name == 'the_template2':
                    return {'code': '<h1>PLOP</h1><a href="*|ARCHIVE|*" target="_blank">Click here or die</a><h2>*|LIST:COMPANY|*</h2>',
                            'name': 'plop newsletter today'}
                return None
        return Obj


# class TestImportTemplate(TestAPIWithLogin):
#     PERMISSIONS = ("author",)
    
#     @patch.object(newsletters.views.mandrill, 'Mandrill', FakeMandrill)
#     def test_template_list(self):
#         response = self.client.get('/secure/api/newsletter/template_list')
#         self.assertEqual(response.status_code, 200)
        
#         self.assertEqual(response.data['content'],
#                          [{'updated_at': datetime.datetime(2014, 1, 2, 6, 10, 2),
#                            'name': 'the_template2'},
#                           {'updated_at': datetime.datetime(2012, 3, 5, 15, 21, 33),
#                            'name': 'template1'}])
    
    
#     @patch.object(newsletters.views.mandrill, 'Mandrill', FakeMandrill)
#     def test_import_template(self):
#         response = self.client.post('/secure/api/newsletter/import_template/the_template2')
#         self.assertEqual(response.status_code, 200)
        
#         self.assertEqual(Newsletter.objects.count(), 1)
#         n = Newsletter.objects.get()
        
#         self.assertEqual(n.subject, "plop newsletter today")
#         self.assertEqual(n.content, '<h1>PLOP</h1><h2>Cook and Be</h2>')
#         self.assertEqual(n.template_name, 'the_template2')
#         self.assertTrue(n.sent_at is None)
#         self.assertTrue(n.sent_by is None)
        
#         response = self.client.post('/secure/api/newsletter/import_template/the_template2')
#         self.assertEqual(response.status_code, 400)
        
#         # The imported template is not anymore in the list
#         response = self.client.get('/secure/api/newsletter/template_list')
#         self.assertEqual(response.status_code, 200)
#         self.assertEqual(len(response.data['content']), 1)
