# -*- coding: utf-8 -*-

from dynpoll.forms import ChoiceForm
from dynpoll.models import Choice, Question, Vote
from django.views.generic.edit import FormView
from django.views.generic.base import TemplateView
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.db.models import Count


class QuestionView(FormView):
    """This view actually displays the question with its Choices and handles
    the actual voting (by using the ChoiceForm-class)."""

    form_class = ChoiceForm
    template_name = 'dynpoll/question.html'

    class QuestionViewError(Exception):
        pass

    def form_valid(self, form):
        """If the form is valid, actually perform the vote."""
        form.perform_vote(request=self.request)

        return super().form_valid(form)

    def get(self, request, question_id, *args, **kwargs):
        """The 'get()'-method is overridden to show the question with its
        answers."""

        if not question_id:
            raise self.QuestionViewError('No question ID was given!')

        # get the Question object
        self.question = get_object_or_404(Question, pk=question_id)

        # get all the choices of this question
        self.choices_list = Choice.objects.filter(question=question_id)

        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):

        # fetch the existing context
        context = super().get_context_data(**kwargs)

        # apply more context!
        context['dynpoll_question'] = self.question

        dynpoll_choices = []
        for choice in self.choices_list:
            dynpoll_choices.append(
                ChoiceForm(data={
                    'question_id': self.question.pk,
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
