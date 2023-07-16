from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import authenticate, login, logout
from django.views.generic import View
from django.contrib import messages
from django.urls import reverse
from django.http import HttpResponseRedirect, HttpRequest
from web.lib import Headscale


class BaseView(LoginRequiredMixin, View):
    login_url = '/login/'
    redirect_field_name = 'next'


class IndexView(BaseView):
    def get(self, request: HttpRequest):
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
        probes = Headscale.get_all_probes()
        return render(request, "web/probes.html", {"probes": probes})


class InfraView(BaseView):
    def get(self, request: HttpRequest):
        nodes = Headscale.get_all_infra()
        print("infra")
        return render(request, "web/infra.html", {"nodes": nodes})
