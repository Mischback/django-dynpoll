# -*- coding: utf-8 -*-

from django import forms

from dynpoll.models import Question, Choice


class ChoiceForm(forms.Form):
    choice_id = forms.IntegerField(widget=forms.HiddenInput)
    question_id = forms.IntegerField(widget=forms.HiddenInput)

    def clean(self):
        """Checks, if the given 'choice_id' is linked to the given
        'question_id'."""

        # get the cleanded data
        cleaned_data = super().clean()

        # get a list of all Choice.pk that are linked to the question
        choices_of_question = Choice.objects.filter(
            question=cleaned_data['question_id']
        ).values_list('pk', flat=True)

        if choice_id not in choices_of_question:
            raise forms.ValidationError('The Choice does not belong to the given question!')

        return cleaned_data

    def perform_vote(self):
        raise Exception('Actually perform the vote!')
