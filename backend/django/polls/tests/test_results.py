from common.test                import TestAPIWithLogin
from polls.tests                import BasePollFixture
from polls.models               import Question, Choice, Answer

class TestQuestions(BasePollFixture, TestAPIWithLogin):
    
    def test_vote_and_get_results(self):
        
        user1 = self.create_db_user()
        user2 = self.create_db_user()
        user3 = self.create_db_user()
        
        Answer.objects.create(user=user1, question=self.q1, choice=self.c1)
        Answer.objects.create(user=user2, question=self.q1, choice=self.c2)
        Answer.objects.create(user=user3, question=self.q1, choice=self.c1)
        
        response = self.client.get('/secure/api/question/%i/results' % self.q1.id)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['question']['title'], "what do you think ok ?")
        
        self.assertEqual(len(response.data['results']), 2)
        self.assertEqual(response.data['results'][0]['choice']['id'], self.c1.id)
        self.assertEqual(response.data['results'][1]['choice']['id'], self.c2.id)
        self.assertEqual(response.data['results'][0]['votes'], 2)
        self.assertEqual(response.data['results'][1]['votes'], 1)
        self.assertEqual(response.data['results'][0]['percentage'], 66.67)
        self.assertEqual(response.data['results'][1]['percentage'], 33.33)
