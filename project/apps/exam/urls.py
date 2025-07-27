from django.urls import path
from . import views

urlpatterns = [
    # Question bank management
    path("questionbank/", views.QuestionBankListView.as_view(), name="questionbank"),
    path("question/create/", views.QuestionCreateView.as_view(), name="question-create"),
    path("question/<int:pk>/update/", views.QuestionUpdateView.as_view(), name="question-update"),
    path("question/<int:pk>/delete/", views.QuestionDeleteView.as_view(), name="question-delete"),
    
    # Exam management
    path("exams/create/", views.ExamCreateView.as_view(), name="exam-create"),
    path("exams/<int:pk>/update/", views.ExamUpdateView.as_view(), name="exam-update"),
    path("exams/<int:pk>/delete/", views.ExamDeleteView.as_view(), name="exam-delete"),
    path("exams/<int:pk>/detail/", views.ExamDetailView.as_view(), name="exam-detail"),
    
    # Question management for exams
    path("add-question/<int:exam_id>/", views.AddQuestionView.as_view(), name="add-question"),
    path("add-question-from-bank/<int:exam_id>/", views.AddQuestionFromBankView.as_view(), name="add-question-from-bank"),
    path("question/<int:pk>/update/<int:exam_id>/", views.QuestionUpdateView.as_view(), name="examquestion-update"),
    path("question/<int:pk>/delete/<int:exam_id>/", views.RemoveQuestionFromExamView.as_view(), name="remove-question"),
    
    # Exam taking
    path("take/<int:exam_id>/", views.TakeExamView.as_view(), name="take"),
    path("myexams/", views.MyExamsView.as_view(), name="myexams"),
    
    # Results and scoring
    path("<int:exam_id>/scores/", views.ExamScoreView.as_view(), name="scores"),
    path("scores/<int:exam_id>/<int:uid>/", views.ExamScoreDetailView.as_view(), name="score-detail"),
    path("scores/<int:pk>/delete/", views.ScoreDeleteView.as_view(), name="score-delete"),
]
