from django.urls import path
from .views import (DashboardAPIView, ZooView,
                    TelegramView, AreaView)

urlpatterns = [
    path("dashboard/",DashboardAPIView.as_view()),
    path('dashboard/<str:serial_id>/', DashboardAPIView.as_view(), name='dashboard-detail-api'),
    path("zoo/",ZooView.as_view()),
    path("area/", AreaView.as_view()),
    path("telegram/",TelegramView.as_view())
]