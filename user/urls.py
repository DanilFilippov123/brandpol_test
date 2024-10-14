from django.urls import path

from user.views import UserAccount, RegistrationFormView

urlpatterns = [
    path('',
         UserAccount.as_view(),
         name='user_account'),
    path('registration/',
         RegistrationFormView.as_view(),
         name='registration')
]
