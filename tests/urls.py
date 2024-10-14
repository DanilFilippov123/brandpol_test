from django.urls import path

from tests.views import TestListView, TestDetailView, RunTestRedirectView, QuestionView, ResultView

urlpatterns = [
    path('all/',
         TestListView.as_view(),
         name='all_tests'),
    path('<int:pk>/',
         TestDetailView.as_view(),
         name='test'),
    path('run/<int:pk>/',
         RunTestRedirectView.as_view(),
         name='run_test'),
    path('run/<int:pk>/question/<int:question_number>',
         QuestionView.as_view(),
         name='question'),
    path('results/<int:pk>',
         ResultView.as_view(),
         name='result'),
]
