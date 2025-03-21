from django.contrib import admin
from .models import Category, QuestionSet, Question, Candidate, Exam, ExamHistory


admin.site.register(Category)
admin.site.register(QuestionSet)
admin.site.register(Question)
admin.site.register(Candidate)
admin.site.register(Exam)
admin.site.register(ExamHistory)
