import boto3
import socket


def parse_ec2_data(ec2_data):
    all_instance_ips = []
    for reservation in ec2_data['Reservations']:
        for item in reservation['Instances']:
            item_keys = list(item.keys())
            if 'PrivateDnsName' in item_keys:
                all_instance_ips.append(item['PrivateDnsName'])
            if 'PrivateIpAddress' in item_keys:
                all_instance_ips.append(item['PrivateIpAddress'])
            if 'PublicDnsName' in item_keys:
                all_instance_ips.append(item['PublicDnsName'])
            if 'PublicIpAddress' in item_keys:
                all_instance_ips.append(item['PublicIpAddress'])
            if 'Ipv6Address' in item_keys:
                all_instance_ips.append(item['Ipv6Address'])
            if 'NetworkInterfaces' in item_keys:
                for network in item['NetworkInterfaces']:
                    network_keys = list(network.keys())
                    if 'Association' in network_keys:
                        association_keys = list(network['Association'])
                        if 'PublicDnsName' in association_keys:
                            all_instance_ips.append(network['Association']['PublicDnsName'])
                        if 'PublicIp' in association_keys:
                            all_instance_ips.append(network['Association']['PublicIp'])
                    if 'Ipv6Addresses' in network_keys:
                        for ipv6 in network['Ipv6Addresses']:
                            if 'Ipv6Address' in list(ipv6.keys()):
                                all_instance_ips.append(ipv6['Ipv6Address'])
                    if 'PrivateIpAddresses' in network_keys:
                        for address in network['PrivateIpAddresses']:
                            association_keys = list(address['Association'])
                            if 'CarrierIp' in association_keys:
                                all_instance_ips.append(address['Association']['CarrierIp'])
                            if 'CustomerOwnedIp' in association_keys:
                                all_instance_ips.append(address['Association']['CustomerOwnedIp'])
                            if 'PublicDnsName' in association_keys:
                                all_instance_ips.append(address['Association']['PublicDnsName'])
                            if 'PublicIp' in association_keys:
                                all_instance_ips.append(address['Association']['PublicIp'])
                            if 'PrivateDnsName' in association_keys:
                                all_instance_ips.append(address['PrivateDnsName'])
                            if 'PrivateIpAddress' in association_keys:
                                all_instance_ips.append(address['PrivateIpAddress'])
    all_instance_ips = list(set(all_instance_ips))
    return all_instance_ips


class EC2:
    def __init__(self, logging):
        self.logging = logging
        self.regions = boto3.session.Session().get_available_regions('ec2')

    def get_ec2_domains_and_ips(self, region: str) -> list:
        """ Gets all load balancers (v2) urls for a given account"""
        marker = ''
        all_instance_ips = []
        self.ec2_client = boto3.client('ec2', region_name=region)
        try:
            response = self.ec2_client.describe_instances(
            )
            all_instance_ips += parse_ec2_data(response)
            if 'NextToken' in list(response.keys()):
                marker = response['NextToken']
        except Exception as e:
            self.logging.warning(f"Boto3 responded with an error - {str(e)}")
        while marker != '':
            try:
                response = self.ec2_client.describe_instances(
                    NextToken=marker
                )
                all_instance_ips += parse_ec2_data(response)
                if 'NextToken' in list(response.keys()):
                    marker = response['NextToken']
                else:
                    marker = ''
            except Exception as e:
                self.logging.error(f"Boto3 responded with an error - {str(e)}")
                break

        return all_instance_ips

    def get_all_ec2_domains_and_ips(self) -> list:
        all_urls = []
        for region in self.regions:
            all_urls += self.get_ec2_domains_and_ips(region)
        return all_urls

    def in_use(self, hostname):
        try:
            socket.getaddrinfo(hostname, 0)
            return True
        except:
            return False

    def ec2check(self, all_domains: list, domain: str) -> dict:
        if domain in all_domains or domain[:-1] in all_domains:
            return {"type": 'good', "message": "EC2 owned by account"}
        elif not self.in_use(domain):
            return {"type": 'issue', "message": "EC2 does not exist"}
        else:
            return {"type": 'warning', "message": "EC2 not in this account"}
