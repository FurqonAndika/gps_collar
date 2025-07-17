from django.urls import path
from .views import UserView,LoginView,LogoutView

urlpatterns = [
    path('account/', UserView.as_view()),
    path('login/', LoginView.as_view()),
    path("logout/",LogoutView.as_view()),
]