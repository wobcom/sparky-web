from sparky_web.settings import HEADSCALE_URL, HEADSCALE_API_KEY
import requests


class Headscale:
    headscale_url = HEADSCALE_URL
    headscale_api_key = HEADSCALE_API_KEY
    request_headers = {
        "Authorization": f"Bearer {headscale_api_key}"
    }

    @staticmethod
    def get_all_nodes() -> list:
        r = requests.get(f"{Headscale.headscale_url}/api/v1/machine", headers=Headscale.request_headers)
        return r.json()['machines']

    @staticmethod
    def get_all_probes() -> list:
        nodes = Headscale.get_all_nodes()
        probes = list(filter(lambda x: x['user']['name'] == 'probes', nodes))
        probes = Headscale.map_routes_to_nodes(probes)
        return probes

    @staticmethod
    def get_all_infra() -> list:
        nodes = Headscale.get_all_nodes()
        nodes = list(filter(lambda x: x['user']['name'] != 'probes', nodes))
        nodes = Headscale.map_routes_to_nodes(nodes)
        return nodes

    @staticmethod
    def get_all_routes():
        r = requests.get(f"{Headscale.headscale_url}/api/v1/routes", headers=Headscale.request_headers)
        return r.json()['routes']

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
        return nodes
