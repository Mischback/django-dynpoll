# -*- coding: utf-8 -*-

# Django imports
from django.db.models import Count
from django.shortcuts import get_object_or_404, render
from django.urls import reverse_lazy
from django.views.generic.base import TemplateView
from django.views.generic.edit import FormView

# app imports
from dynpoll.forms import ChoiceForm, QuestionSequenceManagementForm
from dynpoll.models import Choice, Question, QuestionSequenceItem


class QuestionView(FormView):
    """This view actually displays the question with its Choices and handles
    the actual voting (by using the ChoiceForm-class)."""

    form_class = ChoiceForm
    template_name = 'dynpoll/question.html'

    def form_valid(self, form):
        """If the form is valid, actually perform the vote."""
        form.perform_vote(request=self.request)

        return super().form_valid(form)

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
