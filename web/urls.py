from django.urls import path

from . import views

urlpatterns = [
    path("", views.IndexView.as_view(), name="index"),
    path("probes/", views.ProbesView.as_view(), name="probes"),
    path("infra/", views.InfraView.as_view(), name="infra"),
    path("login/", views.LoginView.as_view(), name="login"),
    path("logout/", views.LogoutView.as_view(), name="logout"),
    path("routes/toggle/", views.ToggleRouteView.as_view(), name="toggle-route"),
]
