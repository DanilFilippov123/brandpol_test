from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import Http404
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.views.generic import ListView, DetailView, RedirectView, TemplateView, FormView

from tests.forms import VariantsFormset
from tests.models import TestModel, UserTestHistoryModel


# Create your views here.

class TestListView(ListView):
    model = TestModel
    template_name = 'tests/all_tests.html'
    context_object_name = 'tests_list'
    paginate_by = 10

    queryset = TestModel.objects.filter(activated=True)


class TestDetailView(LoginRequiredMixin, DetailView):
    model = TestModel
    context_object_name = "test"
    template_name = "tests/test.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['history'] = UserTestHistoryModel.objects.filter(user=self.request.user,
                                                                 test=self.object)
        return context


class RunTestRedirectView(LoginRequiredMixin, RedirectView):
    permanent = False

    def get_redirect_url(self, *args, **kwargs):
        test = get_object_or_404(TestModel, pk=kwargs['pk'])
        self.request.session["current_test"] = {
            "pk": test.pk,
            "name": test.name,
            "theme": test.theme.name,
            "question_count": test.questions.count(),
            "questions": [{
                "name": q.name,
                "answers": dict(),
                "variants": {v.pk: {
                    "name": v.name,
                    "is_correct": v.is_correct
                } for v in q.variants.all()}
            } for q in test.questions.filter(activated=True)]
        }
        return reverse('tests:question', kwargs={
            'pk': test.pk,
            'question_number': 0
        })


class QuestionView(LoginRequiredMixin, FormView):
    template_name = "tests/run_test.html"
    form_class = VariantsFormset

    test = {}
    current_question_number = 0
    quest = {}

    def form_valid(self, form):
        self.check_answer(form)
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['question'] = self.quest
        context['test'] = self.test
        context['question_count'] = self.test['question_count']
        context['current_question'] = self.current_question_number
        context['next_question'] = self.current_question_number + 1
        return context

    def get_initial(self):
        if self.request.method == 'GET':
            return [{
                'name': variant['name'],
                'is_correct': False,
                'pk': pk
            } for pk, variant in self.quest['variants'].items()]
        else:
            return []

    def dispatch(self, request, *args, **kwargs):
        self.test = self.request.session['current_test']
        self.current_question_number = int(kwargs['question_number'])
        self.quest = self.test['questions'][self.current_question_number]

        if (self.test['pk'] != kwargs['pk'] or
                self.current_question_number < 0 or
                self.current_question_number >= self.test['question_count']):
            raise Http404("Question not found")

        return super().dispatch(request, *args, **kwargs)

    def check_answer(self, formset):
        question = (self.request.session
        ['current_test']
        ['questions']
        [self.current_question_number])
        question['answers'] = {}
        for form in formset.forms:
            question['answers'][form.cleaned_data['pk']] = form.cleaned_data['is_correct']
        self.request.session.modified = True

    def get_success_url(self):
        if self.current_question_number + 1 >= self.test['question_count']:
            return reverse('tests:result', kwargs={'pk': self.test['pk']})
        return reverse('tests:question', kwargs={
            'pk': self.test['pk'],
            'question_number': self.current_question_number + 1
        })


class ResultView(LoginRequiredMixin, TemplateView):
    template_name = "tests/result.html"

    def check_result(self):

        test = self.request.session['current_test']

        count_of_correct_answers = len(test['questions'])
        count_of_user_correct_answers = 0

        for quest in test['questions']:
            if all(quest['answers'][pk] == variant['is_correct'] for pk, variant in quest['variants'].items()):
                count_of_user_correct_answers += 1

        return count_of_user_correct_answers / count_of_correct_answers

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['result'] = self.check_result()

        UserTestHistoryModel.objects.create(
            user=self.request.user,
            test_id=self.request.session['current_test']['pk'],
            score=context['result']
        )

        return context

    def post(self, request, *args, **kwargs):
        return self.get(request, *args, **kwargs)
