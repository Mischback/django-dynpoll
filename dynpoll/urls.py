# -*- coding: utf-8 -*-

# Django imports
from django.urls import path

# app imports
from dynpoll.views import QuestionResultView, QuestionView

app_name = 'dynpoll'
urlpatterns = [
    path('<int:question_id>/', QuestionView.as_view(), name='question'),
    path('<int:question_id>/results/', QuestionResultView.as_view(), name='question-result')
]
