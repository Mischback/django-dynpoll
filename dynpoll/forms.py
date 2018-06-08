# -*- coding: utf-8 -*-

# Django imports
from django import forms
from django.conf import settings

# external imports
from ipware import get_client_ip

# app imports
from dynpoll.models import Choice, QuestionSequenceItem, Vote


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


class QuestionSequenceManagementForm(forms.Form):
    """asdf"""

    sequence_item_id = forms.IntegerField(widget=forms.HiddenInput)
    management_action = forms.CharField(widget=forms.HiddenInput)

    def clean(self):
        # get the cleanded data
        cleaned_data = super().clean()

        # actually do some cleaning here!
        if cleaned_data['management_action'] not in (
            'activate-question',
            'deactivate-question',
            'start-voting',
            'stop-voting',
        ):
            # TODO: Is this really the best way? It's backend, after all...
            raise Exception('Unknown action requested!')

        # TODO: verify 'sequence_item_id'!

        return cleaned_data

    def execute_management_action(self):
        """Actually manipulates the models."""

        # TODO: 'get_object_or_404'?
        sequence_item = QuestionSequenceItem.objects.get(pk=self.cleaned_data['sequence_item_id']) or None
        if not sequence_item:
            raise Exception('Could not find QuestionSequenceItem!')

        if 'activate-question' == self.cleaned_data['management_action']:
            # deactivate all other questions...
            # TODO: this might be possible a little less hackish...
            all_seq_items = QuestionSequenceItem.objects.filter(sequence=sequence_item.sequence).filter(is_active=True)
            for item in all_seq_items:
                item.is_active = False
                item.save()

            sequence_item.is_active = True
            sequence_item.save()

        elif 'deactivate-question' == self.cleaned_data['management_action']:
            sequence_item.is_active = False
            sequence_item.voting_allowed = False
            sequence_item.save()

        elif 'start-voting' == self.cleaned_data['management_action']:
            # question must be active to start voting...
            if not sequence_item.is_active:
                raise Exception('You can not start a voting on an inactive question!')

            sequence_item.voting_allowed = True
            sequence_item.save()

        elif 'stop-voting' == self.cleaned_data['management_action']:
            sequence_item.voting_allowed = False
            sequence_item.save()

        else:
            # this can never be reached!
            raise Exception('Unknown action requested!')    # noqa
