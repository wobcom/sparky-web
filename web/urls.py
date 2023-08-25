from django.urls import path

from . import views

urlpatterns = [
    path("", views.IndexView.as_view(), name="index"),
    path("probes/", views.ProbesView.as_view(), name="probes"),
    path("probes/add", views.AddProbeView.as_view(), name="add-probe"),
    path("probes/delete", views.DeleteProbeView.as_view(), name="delete-probe"),
    path("probes/edit", views.EditProbeView.as_view(), name="edit-probe"),
    path("infra/", views.InfraView.as_view(), name="infra"),
    path("login/", views.LoginView.as_view(), name="login"),
    path("logout/", views.LogoutView.as_view(), name="logout"),
    path("routes/toggle", views.ToggleRouteView.as_view(), name="toggle-route"),
    path("api/v1/probe-init", views.APIProbeInitView.as_view(), name="api-probe-init"),
    path("api/v1/probe-update", views.APIProbeUpdateView.as_view(), name="api-probe-update"),
    path("api/v1/metrics-bearer-update", views.APIMetricsBearerUpdateView.as_view(), name="api-metrics-bearer-update"),
]
