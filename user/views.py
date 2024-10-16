from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import TemplateView, FormView

from tests.models import UserTestHistoryModel
from user.forms import RegistrationForm


# Create your views here.

class UserAccount(LoginRequiredMixin, TemplateView):
    template_name = 'user/account.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user'] = self.request.user
        context['recent_tests'] = (UserTestHistoryModel
                                   .objects
                                   .filter(user=self.request.user)
                                   .order_by('-date')[:5])
        return context


class RegistrationFormView(FormView):
    template_name = 'registration/registration.html'
    form_class = RegistrationForm

    def form_valid(self, form):
        res = super().form_valid(form)
        form.save()
        return res

    success_url = reverse_lazy('user:user_account')
