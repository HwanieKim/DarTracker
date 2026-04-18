from django.urls import path
from . import views
urlpatterns = [
    path('list/', views.CorporationListAPI.as_view()),
    path('<str:pk>/', views.CorporationDetailAPI.as_view())
]