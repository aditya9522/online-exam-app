from django.urls import path
from . import views

urlpatterns = [
    path('', views.welcome, name='welcome'),
    path('login/', views.loginUser, name='login'),
    path('register/', views.registerUser, name='register'),
    path('logout/', views.logoutUser, name='logout'),

    path('dashboard/', views.dashboard, name='dashboard'),
    path('categories/', views.categories, name='categories'),
    path('categories/<int:category_id>/edit/', views.editCategory, name='edit-category'),
    path('categories/<int:category_id>/delete/', views.deleteCategory, name='delete-category'),
    
    path('sets/', views.sets, name='sets'),
    path('edit-set/', views.editSet, name='edit-set'),
    path('delete-set/', views.removeSet, name='delete-set'),

    path('questions/', views.questions, name='questions'),
    path('questions/edit/', views.editQuestion, name='edit-question'),
    path('questions/delete/', views.deleteQuestion, name='delete-question'),

    path('candidates/', views.candidates, name='candidates'),
    path('add-candidate/', views.addStudent, name='add-student'),
    path('exam-link/<int:id>/', views.sendExamLink, name='send-exam-link'),
    path('reject/<int:id>/', views.rejectStudent, name='reject-student'),
    
    path('candidate/registration/', views.registerStudent, name='register-candidate'),
    path('candidate/<int:candidate_id>/thankyou/', views.thankyou, name='thankyou'),

    path('exam-login/<int:id>/', views.examLogin, name='exam-login'),
    path('candidate/<int:id>/instructions/', views.instructions, name='exam-instructions'),
    path('candidate/<int:id>/exam-room/', views.examRoom, name='exam-room'),
    path('candidate/<int:id>/submit-exam/', views.submitExam, name='exam-submit'),
    path('candidate/<int:id>/exam-results/', views.examResults, name='exam-results'),
    path('history/', views.history, name='history'),
    path('settings/', views.userSettings, name='settings'),

]
