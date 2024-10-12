from django.views.generic import ListView

from tests.models import TestModel


# Create your views here.

class TestListView(ListView):
    model = TestModel
    template_name = 'tests/all_tests.html'


