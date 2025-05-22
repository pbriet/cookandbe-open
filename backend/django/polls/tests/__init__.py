from polls.models               import Question, Choice, Answer

class BasePollFixture(object):
    """
    base object for creating polls and questions
    """
    
    def setUp(self):
        super().setUp()
        self.q1 = Question.objects.create(author=self.user,
                                          title="what do you think ok ?",
                                          description="just asking...")
        
        self.c1 = Choice.objects.create(question=self.q1, text="toto")
        self.c2 = Choice.objects.create(question=self.q1, text="titi")
        self.c3 = Choice.objects.create(question=self.q1, text="tata")
        
        
        self.q2 = Question.objects.create(author=self.user,
                                          title="what is the best colour ?",
                                          description="")
        
        self.c4 = Choice.objects.create(question=self.q2, text="yellow")
        self.c5 = Choice.objects.create(question=self.q2, text="ni !")