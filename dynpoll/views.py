# -*- coding: utf-8 -*-

# Django imports
from django.conf import settings
from django.db.models import Count
from django.shortcuts import get_object_or_404, render
from django.urls import reverse_lazy
from django.views.generic.base import TemplateView
from django.views.generic.edit import FormView

# external imports
from ipware import get_client_ip

# app imports
from dynpoll.forms import ChoiceForm, QuestionSequenceManagementForm
from dynpoll.models import Choice, Question, QuestionSequenceItem, Vote


class VotingView(FormView):
    """This view just handles everything to actually catch votes.
    DO NOT USE directly!"""

    form_class = ChoiceForm

    def form_valid(self, form):
        """If the form is valid, actually perform the vote."""
        form.perform_vote(request=self.request)

        return super().form_valid(form)


class QuestionView(VotingView):
    """This view actually displays the question with its Choices and handles
    the actual voting (by using the ChoiceForm-class)."""

    template_name = 'dynpoll/question.html'

    def get_context_data(self, **kwargs):

        # fetch the existing context
        context = super().get_context_data(**kwargs)

        question_id = self.kwargs['question_id']

        # apply more context!
        context['dynpoll_question'] = get_object_or_404(Question, pk=question_id)

        choices_list = Choice.objects.filter(question=question_id)
        dynpoll_choices = []
        for choice in choices_list:
            dynpoll_choices.append(
                ChoiceForm(data={
                    'question_id': question_id,
                    'choice_id': choice.pk,
                    'choice_text': choice.choice_text
                })
            )
        context['dynpoll_choices'] = dynpoll_choices

        # return the enhanced context
        return context

    def get_success_url(self):
        return reverse_lazy('dynpoll:question-result', args=[self.kwargs['question_id'], ])


class QuestionResultView(TemplateView):

    template_name = 'dynpoll/question_result.html'

    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)

        question = get_object_or_404(Question, pk=self.kwargs['question_id'])
        context['dynpoll_question'] = question

        choices = Choice.objects.filter(question=question.pk).annotate(Count('vote'))
        context['dynpoll_choices'] = choices

        return context


class QuestionSequenceManagementView(FormView):
    """This view enables control of QuestionSequences."""

    form_class = QuestionSequenceManagementForm

    def get(self, request, *args, **kwargs):

        try:
            sequence_id = self.kwargs['sequence_id']
        except Exception:
            raise

        # find all SequenceItems
        sequence_items = QuestionSequenceItem.objects.filter(sequence=sequence_id)

        # find all associated Questions
        questions = Question.objects.filter(pk__in=sequence_items.values_list('question', flat=True))

        # find all associated Choices
        choices = Choice.objects.filter(question__in=questions.values_list('pk', flat=True))

        # build the context
        context = {}
        context['dynpoll_sequence'] = sequence_items
        context['dynpoll_questions'] = questions
        context['dynpoll_choices'] = choices

        return render(request, 'dynpoll/sequence_management.html', context=context)

    def form_valid(self, form):

        form.execute_management_action()

        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('dynpoll:sequence-management', args=[self.kwargs['sequence_id'], ])


class QuestionSequenceView(VotingView):

    class QuestionSequenceShowResultTrigger(Exception):
        """This exception is raised to control, if the result page has to be
        shown."""

    def get(self, request, *args, **kwargs):

        # get the sequence ID from URL
        try:
            sequence_id = self.kwargs['sequence_id']
        except Exception:
            raise

        # prepare the context
        context = {}
        context['refresh_time'] = 10

        # fetch the currently active sequence item
        try:
            sequence_item = QuestionSequenceItem.objects.filter(is_active=True).get(sequence=sequence_id)
        except QuestionSequenceItem.DoesNotExist:
            return render(request, 'dynpoll/inactive_sequence.html', context=context)

        try:
            # get the question and its answers
            question = get_object_or_404(Question, pk=sequence_item.question.pk)
            choices = Choice.objects.filter(question=question.pk)

            context['dynpoll_question'] = question

            # voting currently in progress, show the voting view
            if not sequence_item.voting_allowed:
                raise self.QuestionSequenceShowResultTrigger

            from_ip = get_client_ip(request)[0]
            votes = Vote.objects.filter(from_ip=from_ip).filter(question=question.pk)
            if votes and not settings.DEBUG:
                raise self.QuestionSequenceShowResultTrigger

            template = 'dynpoll/question.html'

            # actually build the context to enable voting
            dynpoll_choices = []
            for choice in choices:
                dynpoll_choices.append(
                    ChoiceForm(data={
                        'question_id': question.pk,
                        'choice_id': choice.pk,
                        'choice_text': choice.choice_text
                    })
                )
            context['dynpoll_choices'] = dynpoll_choices

        except self.QuestionSequenceShowResultTrigger:
            template = 'dynpoll/question_result.html'

            # determine the actual votes
            choices = choices.annotate(Count('vote'))
            context['dynpoll_choices'] = choices

        return render(request, template, context=context)

    def get_success_url(self):
        return reverse_lazy('dynpoll:sequence', args=[self.kwargs['sequence_id'], ])
