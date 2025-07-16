from django.urls import path
from .views import DashboardAPIView
urlpatterns = [
    path("dashboard/",DashboardAPIView.as_view()),
    path('dashboard/<str:serial_id>/', DashboardAPIView.as_view(), name='dashboard-detail-api'),
]