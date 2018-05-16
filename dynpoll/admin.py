# -*- coding: utf-8 -*-

from django.contrib import admin

from dynpoll.models import Choice, Question, Vote


admin.site.register(Choice)
admin.site.register(Question)
admin.site.register(Vote)
