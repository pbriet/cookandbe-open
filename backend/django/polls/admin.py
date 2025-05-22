from django.contrib     import admin
from polls.models       import Question, Choice


class ChoiceInline(admin.TabularInline):
    model = Choice
    extra = 3

class QuestionAdmin(admin.ModelAdmin):
    list_display = ('title', 'created_at', 'closed_at')
    fieldsets = [
        (None,               {'fields': ['author', 'title', 'description']}),
        ('Dates',            {'fields': ['closed_at']}),
    ]
    inlines = [ChoiceInline]

admin.site.register(Question, QuestionAdmin)