from django.views.generic import ListView, DetailView

from tests.models import TestModel


# Create your views here.

class TestListView(ListView):
    model = TestModel
    template_name = 'tests/all_tests.html'
    context_object_name = 'tests_list'
    paginate_by = 10


class TestDetailView(DetailView):
    model = TestModel
    context_object_name = "test"
    template_name = "tests/test.html"

