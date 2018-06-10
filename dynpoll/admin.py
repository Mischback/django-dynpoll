# -*- coding: utf-8 -*-

# Django imports
from django.contrib import admin

# app imports
from dynpoll.models import (
    Choice, Question, QuestionSequence, QuestionSequenceItem, Vote,
)

admin.site.register(Choice)
admin.site.register(Question)
admin.site.register(Vote)
admin.site.register(QuestionSequence)
admin.site.register(QuestionSequenceItem)
