from django.contrib.auth.models import User
from django.forms.models import model_to_dict
from sparky_web.settings import \
    HEADSCALE_URL, \
    HEADSCALE_API_KEY, \
    TIME_ZONE, \
    PROBE_NIXOS_STATE_VERSION, \
    PROBE_REPO_LOCAL_PATH
from web.models import Probe
from datetime import datetime, timedelta
from git import Repo, Actor
import pytz
import requests
import json
import os


class Headscale:
    headscale_url = HEADSCALE_URL
    headscale_api_key = HEADSCALE_API_KEY
    request_headers = {
        "Authorization": f"Bearer {headscale_api_key}"
    }

    @staticmethod
    def delete_node(node_name: str) -> bool:
        nodes = Headscale.get_all_nodes()
        node = list(filter(lambda x: x['name'] == node_name, nodes))
        if not node:
            return False

        node = node[0]
        node_id = node['id']

        requests.delete(
            f"{Headscale.headscale_url}/api/v1/machine/{node_id}",
            headers=Headscale.request_headers
        )
        return True

    @staticmethod
    def disable_route(route_id: int):
        r = requests.post(
            f"{Headscale.headscale_url}/api/v1/routes/{route_id}/disable",
            headers=Headscale.request_headers
        )
        return True

    @staticmethod
    def enable_route(route_id: int):
        requests.post(
            f"{Headscale.headscale_url}/api/v1/routes/{route_id}/enable",
            headers=Headscale.request_headers
        )
        return True

    @staticmethod
    def expire_probe_pre_auth_key(key: str) -> bool:
        payload = {
            "user": "probes",
            "key": key,
        }
        requests.post(
            f"{Headscale.headscale_url}/api/v1/preauthkey/expire",
            headers=Headscale.request_headers,
            json=payload
        )
        return True

    @staticmethod
    def generate_probe_pre_auth_key() -> str:
        payload = {
            "user": "probes",
            "reusable": False,
            "ephemeral": False,
            "expiration": (datetime.now(tz=pytz.timezone(TIME_ZONE)) + timedelta(hours=1)).isoformat()
        }
        r = requests.post(
            f"{Headscale.headscale_url}/api/v1/preauthkey",
            headers=Headscale.request_headers,
            json=payload
        )
        return r.json()['preAuthKey']['key']

    @staticmethod
    def get_all_nodes() -> list:
        r = requests.get(f"{Headscale.headscale_url}/api/v1/machine", headers=Headscale.request_headers)
        return r.json()['machines']

    @staticmethod
    def get_all_infra() -> list:
        nodes = Headscale.get_all_nodes()
        nodes = list(filter(lambda x: x['user']['name'] != 'probes', nodes))
        nodes = Headscale.map_routes_to_nodes(nodes)
        return nodes

    @staticmethod
    def get_all_probes() -> list:
        nodes = Headscale.get_all_nodes()
        probes = list(filter(lambda x: x['user']['name'] == 'probes', nodes))
        probes = Headscale.map_routes_to_nodes(probes)
        return probes

    @staticmethod
    def get_all_probes_with_live_data() -> list:
        probes_db = Probe.objects.all().order_by('hostname')
        probes_hs = Headscale.get_all_probes()
        probes = list()
        for probe_db in probes_db:
            probe = model_to_dict(probe_db)
            probe['knownToHS'] = False
            probe['hwDisplayName'] = probe_db.hardware.display_name
            for probe_hs in probes_hs:
                if probe_db.hostname == probe_hs['name']:
                    probe['knownToHS'] = True
                    probe['online'] = probe_hs['online']
                    probe['routeEnabled'] = probe_hs['routeEnabled']
                    probe['routeEnabled'] = probe_hs['routeEnabled']
                    probe['routeID'] = probe_hs['routeID']
                    probes_hs.remove(probe_hs)
                    break
            probes.append(probe)
        return probes

    @staticmethod
    def get_all_routes():
        r = requests.get(f"{Headscale.headscale_url}/api/v1/routes", headers=Headscale.request_headers)
        return r.json()['routes']

    @staticmethod
    def get_api_key_expiration() -> timedelta:
        prefix = HEADSCALE_API_KEY[:10]
        r = requests.get(f"{Headscale.headscale_url}/api/v1/apikey", headers=Headscale.request_headers)
        api_keys = r.json()['apiKeys']
        api_key = list(filter(lambda x: x['prefix'] == prefix, api_keys)).pop()
        expiration_time = datetime.fromisoformat(api_key['expiration'])
        return expiration_time - datetime.now(tz=pytz.timezone(TIME_ZONE))

    @staticmethod
    def map_routes_to_nodes(nodes: list) -> list:
        routes = Headscale.get_all_routes()
        for node in nodes:
            for route in routes:
                if route['machine']['id'] == node['id']:
                    node['route'] = route['prefix']
                    node['routeEnabled'] = route['enabled']
                    node['routeID'] = route['id']
                    routes.remove(route)
                    break
        return nodes


class ProbeRepo:
    @staticmethod
    def commit_probe_config(probe: Probe, user: User):
        probe_nixos_config = {
            "config": {
                "networking": {
                    "hostName": probe.hostname
                },
                "profiles": {
                    "sparky-probe": {
                        "enable": True,
                        "ip": probe.ip,
                        "preAuthKey": probe.pre_auth_key,
                        "iperf3": {
                            "enable": probe.test_iperf3,
                            "bandwidthLimit": probe.test_iperf3_bandwidth
                        },
                        "blackbox": {
                            "enable": probe.test_blackbox
                        },
                        "traceroute": {
                            "enable": probe.test_blackbox
                        },
                        "smokeping": {
                            "enable": probe.test_blackbox
                        },
                    }
                },
                "system": {
                    "stateVersion": PROBE_NIXOS_STATE_VERSION
                }
            }
        }
        author = Actor(f"{user.username} (SPARKY-Web)", user.email)
        repo = Repo(PROBE_REPO_LOCAL_PATH)
        repo.remote().pull(rebase=True)
        with open(f"{PROBE_REPO_LOCAL_PATH}/probes/{probe.hostname}_{probe.hardware.slug}.json", "w") as file:
            file.write(json.dumps(probe_nixos_config, indent=4))
        repo.index.add(f"probes/{probe.hostname}_{probe.hardware.slug}.json")
        repo.index.commit(f"SPARKY-Web: (re-)generate {probe.hostname}", author=author, committer=author)
        repo.remote().push().raise_if_error()

    @staticmethod
    def remove_probe_config(probe: Probe, user: User):
        author = Actor(f"{user.username} (SPARKY-Web)", user.email)
        repo = Repo(PROBE_REPO_LOCAL_PATH)
        repo.remote().pull(rebase=True)
        os.remove(f"{PROBE_REPO_LOCAL_PATH}/probes/{probe.hostname}_{probe.hardware.slug}.json")
        repo.index.remove(f"probes/{probe.hostname}_{probe.hardware.slug}.json")
        repo.index.commit(f"SPARKY-Web: remove {probe.hostname}", author=author, committer=author)
        repo.remote().push().raise_if_error()
