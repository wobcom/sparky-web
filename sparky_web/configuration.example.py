SECRET_KEY = 'a very secret key'
ALLOWED_HOSTS = []
CSRF_TRUSTED_ORIGINS = []

# PostgreSQL database configuration
DATABASE = {
    "ENGINE": "django.db.backends.postgresql_psycopg2",
    "NAME": "sparky_web",         # Database name
    "USER": "sparky_web",         # PostgreSQL username
    "PASSWORD": "sparky_web",     # PostgreSQL password
    "HOST": "localhost",          # Database server
    "PORT": "",                   # Database port (leave blank for default)
}

HEADSCALE_URL = "https://headscale.example.com"
HEADSCALE_API_KEY = "example api key"

PROBE_REPO_URL = "https://gitlab.example.com/api/v4/projects/XXX/repository/"
PROBE_REPO_ACCESS_TOKEN = "your access token"

PROBE_NIXOS_STATE_VERSION = "23.05"

PROBE_TAILNET_SUBNET = "fdb0:2a3d:2a4e:3::/64"

PROBE_HOSTNAME_PREFIX = "probe"

METRICS_API_KEY = "long and secure key for the metrics host to fetch the bearer tokens"

PROBE_REPO_LOCAL_PATH = "/path/to/your/probe/repo"

TIME_ZONE = 'Europe/Berlin'
