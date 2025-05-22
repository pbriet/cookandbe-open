from rest_framework.decorators  import api_view
from rest_framework.response    import Response

from django.utils               import timezone
from collections                import defaultdict

from common.decorators          import api_arg, api_model_arg

from polls.models               import Question, Choice, Answer
from polls.serializers          import QuestionSerializer, ChoiceSerializer

@api_view(['GET'])
@api_model_arg('question', Question)
def api_question(request, question):
    has_voted = Answer.objects.filter(question=question, user=request.user).count() > 0
    content = QuestionSerializer(question).data
    content['choices'] = sorted(content['choices'], key=lambda x: x['id'])
    return Response({"has_voted": has_voted,
                     "content": content}, status=200)


@api_view(['POST'])
@api_model_arg('question', Question)
@api_model_arg('choice', Choice)
@api_arg('comment', str, None)
def api_question_vote(request, question, choice, comment):
    
    if choice.question_id != question.id:
        return Response({"status": "error", "details": "this choice does not belong to this question"}, status=400)
    
    if question.closed_at is not None and question.closed_at < timezone.now():
        return Response({"status": "error", "details": "this question has been closed"}, status=400)
    
    if Answer.objects.filter(question=question, user=request.user).count():
        return Response({"status": "error", "details": "you have already answered to this question"}, status=400)
        
    Answer.objects.create(question=question, user=request.user, choice=choice, comment=comment)
    
    return Response({"status": "ok"}, status=200)

@api_view(['GET'])
def api_question_list(request):
    all_questions = Question.objects.all()
    return Response(QuestionSerializer(all_questions, many=True).data)

@api_view(['GET'])
@api_model_arg('question', Question)
def api_question_results(request, question):
    """
    Returns the number of votes per choice, and the aggregated comments for one given question
    """
    res_per_choice = defaultdict(int)
    all_comments = []
    
    for answer in question.answers.all():
        res_per_choice[answer.choice_id] += 1
        if answer.comment:
            all_comments.append(answer.comment)
    
    choices = Choice.objects.filter(id__in=res_per_choice.keys())
    choice_per_id = dict((c.id, c) for c in choices)
    
    # Returning a list of choices, with number of votes and percentage
    res = []
    total_votes = sum(res_per_choice.values())
    if total_votes > 0:
        for choice_id, nb_votes in sorted(res_per_choice.items(), key=lambda x: x[0]):
            serialized_choice = ChoiceSerializer(choice_per_id[choice_id]).data
            res.append({"choice": serialized_choice,
                        "votes": nb_votes,
                        "percentage": round(100*float(nb_votes)/total_votes, 2)})
    
    question = QuestionSerializer(question).data
    
    return Response({"question": question,
                     "comments": all_comments,
                     "results": res}, status=200)