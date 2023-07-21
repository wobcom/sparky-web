from django.db import models
from django.core.validators import MinLengthValidator, RegexValidator


class Probe(models.Model):
    def __str__(self):
        return self.hostname

    hostname = models.CharField(max_length=30, unique=True)
    ip = models.GenericIPAddressField("Tailnet IP", protocol="ipv6", unique=True)
    pre_auth_key = models.CharField(
        "Tailnet PreAuthKey",
        max_length=48,
        validators=[MinLengthValidator(48)],
        unique=True
    )
    is_registered = models.BooleanField(default=False)
    mac_address = models.CharField(
        "MAC Address",
        max_length=17,
        unique=True,
        validators=[
            MinLengthValidator(17),
            RegexValidator(
                regex=r"^([0-9a-f]{2}[:]){5}([0-9a-f]{2})$",
                message="MAC address needs to be a lower-case, colon separated MAC address",
                code="nomatch"
            )
        ]
    )
    api_key = models.CharField("API Key", max_length=32, validators=[MinLengthValidator(32)], unique=True)
    test_iperf3 = models.BooleanField(default=True)
    test_iperf3_bandwidth = models.CharField(
        max_length=5,
        null=True,
        blank=True,
        validators=[
            RegexValidator(
                regex=r"^\d{1,5}[KMG]$",
                message="Expected syntax: #[KMG], where # is the bandwidth limit in bits/s",
                code="nomatch"
            )
        ]
    )

