from django import forms


class ToggleRouteForm(forms.Form):
    route_id = forms.IntegerField()
    route_id.widget = route_id.hidden_widget()
    route_enabled = forms.BooleanField(required=False)
    route_enabled.widget = route_enabled.hidden_widget()
