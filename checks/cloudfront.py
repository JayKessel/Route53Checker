import boto3
import socket


class Cloudfront:
    def __init__(self, logging):
        self.logging = logging
        self.cloudfront_client = boto3.client('cloudfront')

    def get_distributions(self) -> list:
        """ Gets all distribution urls for a given account"""
        marker = ''
        returned_distributions = []
        self.apigateway_client = boto3.client('apigatewayv2')
        try:
            response = self.cloudfront_client.list_distributions(
                MaxItems='100'
            )
            for item in response['DistributionList']['Items']:
                returned_distributions.append(item['DomainName'].lower())
            if 'NextMarker' in list(response['DistributionList'].keys()):
                marker = response['DistributionList']['NextMarker']
        except Exception as e:
            self.logging.warning(f"Boto3 responded with an error - {str(e)}")
        while marker != '':
            try:
                response = self.cloudfront_client.list_distributions(
                    MaxItems='100',
                    Marker=marker
                )
                for item in response['DistributionList']['Items']:
                    returned_distributions.append(item['DomainName'].lower())
                if 'NextMarker' in list(response['DistributionList'].keys()):
                    marker = response['DistributionList']['NextMarker']
                else:
                    marker = ''
            except Exception as e:
                self.logging.error(f"Boto3 responded with an error - {str(e)}")
                break

        return returned_distributions

    def gateway_in_use(self, hostname):
        try:
            socket.getaddrinfo(hostname, 0)
            return True
        except:
            return False

    def cloudfront_check(self, all_domains: list, domain: str) -> dict:
        if domain in all_domains or domain[:-1] in all_domains:
            return {"type": 'good', "message": "Cloudfront domain owned by account"}
        elif not self.gateway_in_use(domain):
            return {"type": 'issue', "message": "Cloudfront domain does not exist"}
        else:
            return {"type": 'warning', "message": "Cloudfront domain owned by another account"}
