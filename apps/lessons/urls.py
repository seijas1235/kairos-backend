"""
URL routing for lessons app.
"""
from django.urls import path
from . import views

urlpatterns = [
    path('generate/', views.generate_lesson, name='generate_lesson'),
    path('adapt/', views.adapt_content, name='adapt_content'),
]
