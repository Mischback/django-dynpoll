# -*- coding: utf-8 -*-

# Django imports
from django.db import models


class Question(models.Model):
    question_text = models.CharField(max_length=200)

    def __str__(self):
        return self.question_text


class Choice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    choice_text = models.CharField(max_length=200)

    def __str__(self):
        return self.choice_text


class Vote(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    choice = models.ForeignKey(Choice, on_delete=models.CASCADE)
    from_ip = models.GenericIPAddressField()

    def __str__(self):
        return 'Vote on [Choice {}] from {}'.format(self.choice.pk, self.from_ip)


class QuestionSequence(models.Model):
    name = models.CharField(max_length=200)

    def __str__(self):
        return self.name


class QuestionSequenceItem(models.Model):
    sequence = models.ForeignKey(QuestionSequence, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.SET_NULL, null=True)
    order = models.SmallIntegerField(default=1)
    is_active = models.BooleanField(default=False)
    voting_allowed = models.BooleanField(default=False)

    class Meta:
        unique_together = ('sequence', 'question')

    def __str__(self):
        return '[{}] {} - {}'.format(self.sequence, self.order, self.question)
