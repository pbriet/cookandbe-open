from common.test                import TestAPIWithLogin
from polls.tests                import BasePollFixture
from polls.models               import Question, Choice, Answer

class TestQuestions(BasePollFixture, TestAPIWithLogin):
    
        
    def test_get_question(self):
        response = self.client.get('/api/question/%i' % self.q1.id)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['has_voted'], False)
        self.assertEqual(response.data['content']['title'], "what do you think ok ?")
        self.assertEqual(len(response.data['content']['choices']), 3)
        self.assertEqual(response.data['content']['choices'][1]["text"], "titi")

    def test_get_question_voted(self):
        """
        Test that the API correctly returns when the question has already been answered by this user
        """
        Answer.objects.create(question=self.q1, choice=self.c2, user=self.user)
        
        response = self.client.get('/api/question/%i' % self.q1.id)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['has_voted'], True)
        
        