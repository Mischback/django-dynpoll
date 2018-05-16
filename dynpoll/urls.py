# -*- coding: utf-8 -*-

from django.urls import path

from dynpoll.views import QuestionView, QuestionResultView


app_name = 'dynpoll'
urlpatterns = [
    path('<int:question_id>/', QuestionView.as_view(), name='question'),
    path('<int:question_id>/results/', QuestionResultView.as_view(), name='question-result')
]
