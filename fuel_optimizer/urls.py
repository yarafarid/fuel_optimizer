from django.urls import path
from . import views

urlpatterns = [
    path('routes/', views.RouteOptimizationView.as_view(), name='my-endpoint'),
]