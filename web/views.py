from django.db import IntegrityError
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
from web.lib import Headscale, ProbeRepo
from web.forms import \
    AddProbeForm, \
    DeleteProbeForm, \
    EditProbeForm, \
    ToggleRouteForm
from web.models import Probe, ProbeHardware
import random
import string
import macaddress
from sparky_web.settings import \
    API_KEY_EXPIRATION_DAYS_WARNING, \
    API_KEY_EXPIRATION_DAYS_CRITICAL, \
    PROBE_REPO_URL, \
    PROBE_REPO_ACCESS_TOKEN, \
    PROBE_TAILNET_SUBNET, \
    PROBE_HOSTNAME_PREFIX, \
    METRICS_API_KEY


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
        add_probe_form = AddProbeForm()
        delete_probe_form = DeleteProbeForm()
        edit_probe_form = EditProbeForm()
        toggle_route_form = ToggleRouteForm()
        return render(
            request,
            "web/probes.html",
            {
                "probes": probes,
                "add_probe_form": add_probe_form,
                "delete_probe_form": delete_probe_form,
                "edit_probe_form": edit_probe_form,
                "toggle_route_form": toggle_route_form,
            }
        )


class AddProbeView(BaseView):
    def post(self, request: HttpRequest):
        form = AddProbeForm(data=request.POST)
        if not form.is_valid():
            messages.add_message(request, messages.ERROR, "Form invalid")
            return HttpResponseRedirect(reverse("probes"))
        try:
            mac = macaddress.MAC(form.cleaned_data['mac_address'])
        except (ValueError, TypeError):
            messages.add_message(request, messages.ERROR, "Invalid MAC address format")
            return HttpResponseRedirect(reverse("probes"))
        mac = str(mac).replace("-", ":").lower()
        probes = Probe.objects.all()
        used_probe_nos = list()
        used_probe_ips = list()
        for probe in probes:
            probe_no = int(probe.hostname[-2:])
            used_probe_nos.append(probe_no)
            used_probe_ips.append(probe.ip)
        next_probe_no = (i for i in range(1, 99) if i not in used_probe_nos)
        next_probe_no = next(next_probe_no)
        next_probe_no = str(next_probe_no).zfill(2)
        next_probe_ip = (host for host in PROBE_TAILNET_SUBNET.hosts() if str(host) not in used_probe_ips)
        next_probe_ip = str(next(next_probe_ip))
        pre_auth_key = Headscale.generate_probe_pre_auth_key()
        api_key = ''.join(random.choices(string.ascii_letters + string.digits, k=32))
        metrics_bearer = ''.join(random.choices(string.ascii_letters + string.digits, k=32))
        bandwidth_limit = form.cleaned_data['iperf3_bandwidth_limit']
        if not bandwidth_limit:
            bandwidth_limit = None
        probe = Probe()
        probe.hardware = form.cleaned_data['hardware']
        probe.hostname = PROBE_HOSTNAME_PREFIX + next_probe_no
        probe.ip = next_probe_ip
        probe.pre_auth_key = pre_auth_key
        probe.metrics_bearer = metrics_bearer
        probe.api_key = api_key
        probe.mac_address = mac
        probe.test_iperf3 = form.cleaned_data['iperf3_enabled']
        probe.test_iperf3_bandwidth = bandwidth_limit
        try:
            probe.save()
        except IntegrityError:
            Headscale.expire_probe_pre_auth_key(pre_auth_key)
            messages.add_message(
                request,
                messages.ERROR,
                "Probe with this name, IP or MAC-Address already exists. Please check your inputs and try again."
            )
            return HttpResponseRedirect(reverse("probes"))
        try:
            ProbeRepo.commit_probe_config(probe, request.user)
        except Exception:
            messages.add_message(request, messages.ERROR, "Error while adding the probe to the config repo.")
            return HttpResponseRedirect(reverse("probes"))
        return HttpResponseRedirect(reverse("probes"))


class DeleteProbeView(BaseView):
    def post(self, request: HttpRequest):
        form = DeleteProbeForm(data=request.POST)
        if not form.is_valid():
            messages.add_message(request, messages.ERROR, "Form invalid")
            return HttpResponseRedirect(reverse("probes"))
        probe = Probe.objects.get(pk=form.cleaned_data['probe_id'])
        hostname = probe.hostname
        pre_auth_key = probe.pre_auth_key
        try:
            ProbeRepo.remove_probe_config(probe, request.user)
        except Exception:
            messages.add_message(request, messages.ERROR, "Error while removing the probe from the config repo.")
            return HttpResponseRedirect(reverse("probes"))
        Headscale.expire_probe_pre_auth_key(pre_auth_key)
        Headscale.delete_node(hostname)
        probe.delete()
        messages.add_message(request, messages.SUCCESS, f"Deleted probe {hostname}")
        return HttpResponseRedirect(reverse("probes"))


class EditProbeView(BaseView):
    def post(self, request: HttpRequest):
        form = EditProbeForm(data=request.POST)
        if not form.is_valid():
            messages.add_message(request, messages.ERROR, "Form invalid")
            return HttpResponseRedirect(reverse("probes"))
        probe = Probe.objects.get(pk=form.cleaned_data['probe_id'])
        probe.test_iperf3 = form.cleaned_data["iperf3_enabled"]
        bandwidth_limit = form.cleaned_data['iperf3_bandwidth_limit']
        if not bandwidth_limit:
            bandwidth_limit = None
        probe.test_iperf3_bandwidth = bandwidth_limit
        probe.save()
        try:
            ProbeRepo.commit_probe_config(probe, request.user)
        except Exception:
            messages.add_message(request, messages.ERROR, "Error while editing the probe in the config repo.")
            return HttpResponseRedirect(reverse("probes"))
        messages.add_message(request, messages.SUCCESS, f"Edited probe {probe.hostname}")
        return HttpResponseRedirect(reverse("probes"))


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
                "metrics-bearer": probe.metrics_bearer,
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
                "metrics-bearer": probe.metrics_bearer,
            }
        }
        return JsonResponse(data)


class APIMetricsBearerUpdateView(APIView):
    def post(self, request: HttpRequest):
        metrics_api_key = request.POST.get("metrics-api-key")
        if metrics_api_key != METRICS_API_KEY:
            data = {
                "status": "unauthorized",
                "message": "Invalid Metrics API Key"
            }
            return JsonResponse(data, status=403)
        probes = Probe.objects.all()
        bearer_data = list()
        for probe in probes:
            probe_bearer_data = {
                "bearer_token": probe.metrics_bearer,
                "url_prefix": f"http://localhost:8428/api/v1/write?extra_label=instance={probe.hostname}"
            }
            bearer_data.append(probe_bearer_data)
        data = {
            "status": "ok",
            "data": {
                "users": bearer_data
            }
        }
        return JsonResponse(data)
