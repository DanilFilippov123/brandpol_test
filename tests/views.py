from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.views.generic import ListView, DetailView, RedirectView, TemplateView, FormView

from tests.forms import VariantsFormset
from tests.models import TestModel, UserTestHistoryModel, ThemeModel


# Create your views here.

class TestListView(ListView):
    model = TestModel
    template_name = 'tests/all_tests.html'
    context_object_name = 'tests_list'
    paginate_by = 10

    queryset = TestModel.objects.filter(activated=True).order_by('pk')

    def get_queryset(self):
        theme = self.request.GET.get('theme')
        if theme is not None:
            if theme == '__all__':
                self.queryset = TestModel.objects.all()
            else:
                self.queryset = TestModel.objects.filter(theme_id=int(theme))
        return self.queryset

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['themes'] = ThemeModel.objects.all()
        return context


class TestDetailView(LoginRequiredMixin, DetailView):
    model = TestModel
    context_object_name = "test"
    template_name = "tests/test.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user_history'] = UserTestHistoryModel.objects.filter(user=self.request.user,
                                                                 test=self.object)
        return context


class RunTestRedirectView(LoginRequiredMixin, RedirectView):
    permanent = False

    def get_redirect_url(self, *args, **kwargs):
        test = get_object_or_404(TestModel, pk=kwargs['pk'])
        if test.questions.count() == 0:
            return reverse('tests:test', kwargs={'pk': test.pk})
        self.request.session["current_test"] = {
            "pk": test.pk,
            "name": test.name,
            "theme": test.theme.name,
            "question_count": test.questions.filter(activated=True).count(),
            "questions": [{
                "pk": q.pk,
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
        context['questions'] = self.test['questions']
        context['test'] = self.test
        context['question_count'] = self.test['question_count']
        context['current_question'] = self.current_question_number
        context['next_question'] = self.current_question_number + 1
        return context

    def get_initial(self):
        if self.request.method == 'GET':
            return [{
                'name': variant['name'],
                'is_correct': self.quest['answers'][pk] if pk in self.quest['answers'] else False,
                'pk': pk
            } for pk, variant in self.quest['variants'].items()]
        else:
            return []

    def dispatch(self, request, *args, **kwargs):
        self.test = self.request.session['current_test']

        if self.test is None:
            return redirect('tests:test', pk=kwargs['pk'])

        self.current_question_number = int(kwargs['question_number'])
        if not (0 <= self.current_question_number < len(self.test['questions'])):
            pass
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
    test = {}

    def check_result(self):

        self.test = self.request.session['current_test']

        count_of_correct_answers = len(self.test['questions'])
        count_of_user_correct_answers = 0

        for quest in self.test['questions']:
            if all(quest['answers'].get(pk, False) == variant['is_correct']
                   for pk, variant in quest['variants'].items()):
                count_of_user_correct_answers += 1

        return round(count_of_user_correct_answers / count_of_correct_answers * 100)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['result'] = self.check_result()
        context['test'] = self.test

        context['best'] = UserTestHistoryModel.objects.filter(
            test_id=self.test['pk'],
            user=self.request.user
        ).order_by('-score')[:5]

        UserTestHistoryModel.objects.create(
            user=self.request.user,
            test_id=self.test['pk'],
            score=context['result']
        )

        return context

    def post(self, request, *args, **kwargs):
        return self.get(request, *args, **kwargs)
