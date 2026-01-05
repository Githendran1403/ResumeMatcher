from django.urls import path
from . import views

urlpatterns = [
    path('', views.multi_upload_view, name='multi_upload'),  # Default route
    path('multi/', views.multi_upload_view, name='multi_upload'),
    path('multi-match/', views.multi_match_view, name='multi_match'),
]
