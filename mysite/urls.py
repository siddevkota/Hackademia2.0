from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('courses', views.courses, name='courses'),
    path('pricing', views.pricing, name='pricing'),
    path('Courses/<str:slug>', views.course_detail, name='course_detail'),
    path('Courses/checkout/<str:slug>', views.Checkout, name='Checkout'),
    path('Courses/<str:slug>/<str:lecture_slug>', views.lecture_detail, name='lecture_detail'),
    path('course/<slug:slug>/lecture/<slug:lecture_slug>/simplified/', views.simplified_explanation, name='simplified_explanation'),
    path('courses/lecture/comment', views.videoComment, name='videoComment'),
    # path('courses/quiz/<int:section_id>/', views.quiz_page, name='quiz_page'),
    path('quiz/<int:section_id>/', views.quiz_page, name='quiz_page'),
    path('quiz/<int:section_id>/submit/', views.submit_quiz, name='submit_quiz'),
    # path('flowise/<path:path>/', views.flowise_proxy, name='flowise_proxy'),
]
