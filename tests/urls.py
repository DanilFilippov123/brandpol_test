from django.urls import path

from tests.views import TestListView

urlpatterns = [
    path('all/',
         TestListView.as_view(),
         name='all_tests'),
]
