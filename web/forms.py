from django import forms
from django.core.validators import RegexValidator


class ToggleRouteForm(forms.Form):
    route_id = forms.IntegerField()
    route_id.widget = route_id.hidden_widget()
    route_enabled = forms.BooleanField(required=False)
    route_enabled.widget = route_enabled.hidden_widget()


class AddProbeForm(forms.Form):
    mac_address = forms.CharField(
        label="MAC address of the probe",
        max_length=17,
        min_length=12,
        widget=forms.TextInput(attrs={'placeholder': 'aa:bb:cc:dd:ee:ff'})
    )
    iperf3_enabled = forms.BooleanField(
        label="Enable iperf3 tests",
        required=False,
        widget=forms.CheckboxInput(attrs={'checked': 'true'})
    )
    iperf3_bandwidth_limit = forms.CharField(
        label="iperf3 bandwidht limit (optional)",
        widget=forms.TextInput(attrs={'placeholder': '100M'}),
        required=False,
        validators=[
            RegexValidator(
                regex=r"^\d{1,5}[KMG]$",
                message="Expected syntax: #[KMG], where # is the bandwidth limit in bits/s",
                code="nomatch"
            )
        ]
    )
