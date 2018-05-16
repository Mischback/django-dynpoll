# -*- coding: utf-8 -*-

from django.conf import settings
from django import forms
from ipware import get_client_ip

from dynpoll.models import Choice, Vote


class ChoiceForm(forms.Form):
    choice_id = forms.IntegerField(widget=forms.HiddenInput)
    choice_text = forms.CharField(widget=forms.HiddenInput, required=False)
    question_id = forms.IntegerField(widget=forms.HiddenInput)

    def clean(self):
        """Checks, if the given 'choice_id' is linked to the given
        'question_id'."""

        # get the cleanded data
        cleaned_data = super().clean()

        # get a list of all Choice.pk that are linked to the question
        self.choices_of_question = Choice.objects.filter(
            question=cleaned_data['question_id']
        ).values_list('pk', flat=True)

        if cleaned_data['choice_id'] not in self.choices_of_question:
            raise forms.ValidationError('The Choice does not belong to the given question!')

        return cleaned_data

    def perform_vote(self, request):
        try:
            choice = Choice.objects.get(pk=self.cleaned_data['choice_id'])
        except Choice.DoesNotExist:
            raise Exception('Choice does not exist!')

        from_ip = get_client_ip(request)[0]
        if not settings.DEBUG:
            votes = Vote.objects.filter(
                choice__in=self.choices_of_question
            ).values_list('from_ip', flat=True)

            if from_ip in votes:
                # TODO: don't raise error, simply redirect to result page!
                raise forms.ValidationError('You already voted on this question!')

        vote = Vote.objects.create(choice=choice, from_ip=from_ip)  # noqa
