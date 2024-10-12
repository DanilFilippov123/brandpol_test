from django.urls import path

from tests.views import TestListView, TestDetailView

urlpatterns = [
    path('all/',
         TestListView.as_view(),
         name='all_tests'),
    path('<int:pk>/',
         TestDetailView.as_view(),
         name='test')
]
