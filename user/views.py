from django.urls import reverse_lazy
from django.views.generic import TemplateView, FormView

from user.forms import RegistrationForm


# Create your views here.

class UserAccount(TemplateView):
    template_name = 'user/account.html'


class RegistrationFormView(FormView):
    template_name = 'registration/registration.html'
    form_class = RegistrationForm

    success_url = reverse_lazy('user:user_account')
