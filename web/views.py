from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import authenticate, login, logout
from django.views.generic import View
from django.contrib import messages
from django.urls import reverse
from django.http import HttpResponseRedirect, HttpRequest, JsonResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from web.lib import Headscale
from web.forms import ToggleRouteForm
from web.models import Probe
from sparky_web.settings import \
    API_KEY_EXPIRATION_DAYS_WARNING, \
    API_KEY_EXPIRATION_DAYS_CRITICAL, \
    PROBE_REPO_URL, \
    PROBE_REPO_ACCESS_TOKEN


@method_decorator(csrf_exempt, name='dispatch')
class APIView(View):
    pass

class BaseView(LoginRequiredMixin, View):
    login_url = '/login/'
    redirect_field_name = 'next'


class IndexView(BaseView):
    def get(self, request: HttpRequest):
        api_key_expiration_days = Headscale.get_api_key_expiration().days
        if api_key_expiration_days <= API_KEY_EXPIRATION_DAYS_CRITICAL:
            messages.add_message(
                request,
                messages.ERROR,
                f"The API Key expires in {api_key_expiration_days} days. Please renew it as soon as possible."
            )
        elif api_key_expiration_days <= API_KEY_EXPIRATION_DAYS_WARNING:
            messages.add_message(
                request,
                messages.WARNING,
                f"The API Key expires in {api_key_expiration_days} days. Please renew it timely."
            )
        return render(request, "web/index.html")


class LoginView(View):
    def get(self, request: HttpRequest):
        next_url = request.GET.get("next")
        if request.user.is_authenticated:
            if next_url:
                return HttpResponseRedirect(next_url)
            else:
                return HttpResponseRedirect(reverse("index"))
        form = AuthenticationForm()
        return render(request, "web/login.html", {"form": form, "next": next_url})

    def post(self, request: HttpRequest):
        form = AuthenticationForm(data=request.POST)
        if not form.is_valid():
            messages.add_message(request, messages.ERROR, "Login failed")
            return HttpResponseRedirect(reverse("login"))
        username = form.cleaned_data["username"]
        password = form.cleaned_data["password"]
        user = authenticate(request, username=username, password=password)
        if user is not None:
            messages.add_message(request, messages.SUCCESS, "Login successful")
            login(request, user)
            next_url = request.POST.get("next")
            if next_url:
                return HttpResponseRedirect(next_url)
            else:
                return HttpResponseRedirect(reverse("index"))
        else:
            messages.add_message(request, messages.ERROR, "Login failed")
            return HttpResponseRedirect(reverse("login"))


class LogoutView(View):
    def get(self, request: HttpRequest):
        logout(request)
        return HttpResponseRedirect(reverse("login"))


class ProbesView(BaseView):
    def get(self, request: HttpRequest):
        probes = Headscale.get_all_probes_with_live_data()
        toggle_route_form = ToggleRouteForm()
        return render(request, "web/probes.html", {"probes": probes, "toggle_route_form": toggle_route_form})


class ToggleRouteView(BaseView):
    def post(self, request: HttpRequest):
        form = ToggleRouteForm(data=request.POST)
        if not form.is_valid():
            messages.add_message(request, messages.ERROR, "Form invalid")
            return HttpResponseRedirect(reverse("probes"))
        route_id = int(form.cleaned_data["route_id"])
        route_enabled = bool(form.cleaned_data["route_enabled"])
        if route_enabled:
            Headscale.disable_route(route_id)
        else:
            Headscale.enable_route(route_id)
        return HttpResponseRedirect(reverse("probes"))


class InfraView(BaseView):
    def get(self, request: HttpRequest):
        nodes = Headscale.get_all_infra()
        print("infra")
        return render(request, "web/infra.html", {"nodes": nodes})


class APIProbeInitView(APIView):
    def post(self, request: HttpRequest):
        mac = request.POST.get("mac")
        probe = Probe.objects.filter(mac_address=mac)
        if not probe:
            data = {
                "status": "unauthorized",
                "message": "Invalid MAC address"
            }
            return JsonResponse(data, status=403)
        probe = probe[0]
        if probe.is_registered:
            data = {
                "status": "unauthorized",
                "message": "Probe is already registered"
            }
            return JsonResponse(data, status=403)
        probe.is_registered = True
        probe.save()
        data = {
            "status": "ok",
            "data": {
                "hostname": probe.hostname,
                "repo-url": PROBE_REPO_URL,
                "access-token": PROBE_REPO_ACCESS_TOKEN,
                "api-key": probe.api_key,
            }
        }
        return JsonResponse(data)


class APIProbeUpdateView(APIView):
    def post(self, request: HttpRequest):
        api_key = request.POST.get("api-key")
        probe = Probe.objects.filter(api_key=api_key)
        if not probe:
            data = {
                "status": "unauthorized",
                "message": "Invalid API Key"
            }
            return JsonResponse(data, status=403)
        probe = probe[0]
        data = {
            "status": "ok",
            "data": {
                "hostname": probe.hostname,
                "repo-url": PROBE_REPO_URL,
                "access-token": PROBE_REPO_ACCESS_TOKEN,
            }
        }
        return JsonResponse(data)
