
from django.utils               import timezone

from common.test                import TestAPIWithLogin

from polls.tests                import BasePollFixture
from polls.models               import Question, Choice, Answer

import datetime

class TestAnswers(BasePollFixture, TestAPIWithLogin):
    
    def _vote(self, choice=None):
        if choice is None:
            choice = self.c2
        return self.client.post('/api/question/%i/vote' % self.q1.id,
                                    {'choice_id': choice.id, 'comment': 'Plop!'})
    
    def test_vote(self):
        response = self._vote()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Answer.objects.count(), 1)
        
        # Already voted !
        response = self._vote(self.c3)
        self.assertEqual(response.status_code, 400)
        
   
    def test_vote_question_closed(self):
        self.q1.closed_at = timezone.now() - datetime.timedelta(days=1)
        self.q1.save()
        response = self._vote()
        self.assertEqual(response.status_code, 400)

        
    def test_vote_question_not_closed_yet(self):
        self.q1.closed_at = timezone.now() + datetime.timedelta(days=1)
        self.q1.save()
        response = self._vote()
        self.assertEqual(response.status_code, 200)

    def test_vote_question_not_a_good_choice(self):
        response = self._vote(self.c4)
        self.assertEqual(response.status_code, 400)
        