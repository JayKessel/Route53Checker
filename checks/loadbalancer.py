import boto3
import socket


class Loadbalancer:
    def __init__(self, logging):
        self.logging = logging
        self.regions = boto3.session.Session().get_available_regions('elbv2')

    def get_loadbalancersv2(self, region: str) -> list:
        """ Gets all load balancers (v2) urls for a given account"""
        marker = ''
        returned_distributions = []
        self.loadbalancerv2 = boto3.client('elbv2', region_name=region)
        try:
            response = self.loadbalancerv2.describe_load_balancers(
            )
            for item in response['LoadBalancers']:
                returned_distributions.append(item['DNSName'].lower())
            if 'NextMarker' in list(response.keys()):
                marker = response['NextMarker']
        except Exception as e:
            self.logging.warning(f"Boto3 responded with an error - {str(e)}")
        while marker != '':
            try:
                response = self.loadbalancerv2.describe_load_balancers(
                    Marker=marker
                )
                for item in response['LoadBalancers']:
                    returned_distributions.append(item['DNSName'].lower())
                if 'NextMarker' in list(response.keys()):
                    marker = response['NextMarker']
                else:
                    marker = ''
            except Exception as e:
                self.logging.error(f"Boto3 responded with an error - {str(e)}")
                break

        return returned_distributions

    def get_loadbalancersv1(self, region: str) -> list:
        """ Gets all load balancers (v1) urls for a given account"""
        marker = ''
        returned_distributions = []
        self.loadbalancerv1 = boto3.client('elb', region_name=region)
        try:
            response = self.loadbalancerv1.describe_load_balancers(
            )
            for item in response['LoadBalancerDescriptions']:
                returned_distributions.append(item['DNSName'].lower())
            if 'NextMarker' in list(response.keys()):
                marker = response['NextMarker']
        except Exception as e:
            self.logging.warning(f"Boto3 responded with an error - {str(e)}")
        while marker != '':
            try:
                response = self.loadbalancerv1.describe_load_balancers(
                    Marker=marker
                )
                for item in response['LoadBalancerDescriptions']:
                    returned_distributions.append(item['DNSName'].lower())
                if 'NextMarker' in list(response.keys()):
                    marker = response['NextMarker']
                else:
                    marker = ''
            except Exception as e:
                self.logging.error(f"Boto3 responded with an error - {str(e)}")
                break

        return returned_distributions

    def get_all_loadbalancers(self) -> list:
        all_urls = []
        for region in self.regions:
            all_urls += self.get_loadbalancersv2(region)
            all_urls += self.get_loadbalancersv1(region)
        return all_urls

    def in_use(self, hostname):
        try:
            socket.getaddrinfo(hostname, 0)
            return True
        except:
            return False

    def loadbalancercheck(self, all_domains: list, domain: str) -> dict:
        if domain in all_domains or domain[:-1] in all_domains:
            return {"type": 'good', "message": "Loadbalancer owned by account"}
        elif not self.in_use(domain):
            return {"type": 'issue', "message": "Loadbalancer does not exist"}
        else:
            return {"type": 'warning', "message": "Loadbalancer owned by another account"}
