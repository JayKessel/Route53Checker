import boto3
import socket


class APIGateway:
    """ Checks APIGateway resources in Route 53 records """
    def __init__(self, logging):
        self.apigateway_client = None
        self.logging = logging
        self.regions_v1 = boto3.session.Session().get_available_regions('apigateway')
        self.regions_v2 = boto3.session.Session().get_available_regions('apigatewayv2')

    def get_api_endpoints_v2(self, region: str) -> list:
        next_token = ''
        returned_api_urls = []
        self.apigateway_client = boto3.client('apigatewayv2', region_name=region)
        try:
            response = self.apigateway_client.get_apis(
                MaxResults='100'
            )
            for item in response['Items']:
                returned_api_urls.append(item['ApiEndpoint'].replace("https://", "").lower())
            if 'NextToken' in list(response.keys()):
                next_token = response['NextToken']
        except Exception as e:
            self.logging.warning(f"Boto3 responded with an error - {str(e)}")
        while next_token != '':
            try:
                response = self.apigateway_client.get_apis(
                    MaxResults='100',
                    NextToken=next_token
                )
                for item in response['Items']:
                    returned_api_urls.append(item['ApiEndpoint'].replace("https://", "").lower())
                if 'NextToken' in list(response.keys()):
                    next_token = response['NextToken']
                else:
                    next_token = ''
            except Exception as e:
                self.logging.error(f"Boto3 responded with an error - {str(e)}")
                break
        return returned_api_urls

    def get_api_endpoints_v1(self, region: str) -> list:
        next_token = ''
        returned_api_urls = []
        self.apigateway_client = boto3.client('apigateway', region_name=region)
        try:
            response = self.apigateway_client.get_domain_names(
                limit='100'
            )
            for item in response['Items']:
                returned_api_urls.append(item['domainName'].replace("https://", "").lower())
                returned_api_urls.append(item['regionalDomainName'].lower())
                returned_api_urls.append(item['distributionDomainName'].lower())
            if 'position' in list(response.keys()):
                next_token = response['position']
        except Exception as e:
            self.logging.warning(f"Boto3 responded with an error - {str(e)}")
        while next_token != '':
            try:
                response = self.apigateway_client.get_domain_names(
                    limit='100',
                    position=next_token
                )
                for item in response['Items']:
                    returned_api_urls.append(item['domainName'].replace("https://", "").lower())
                    returned_api_urls.append(item['regionalDomainName'].lower())
                    returned_api_urls.append(item['distributionDomainName'].lower())
                if 'position' in list(response.keys()):
                    next_token = response['position']
                else:
                    next_token = ''
            except Exception as e:
                self.logging.error(f"Boto3 responded with an error - {str(e)}")
                break
        return returned_api_urls

    def get_all_endpoints(self) -> list:
        all_urls = []
        for region in self.regions_v1:
            all_urls += self.get_api_endpoints_v1(region)
        for region in self.regions_v2:
            all_urls += self.get_api_endpoints_v2(region)
        return all_urls

    def gateway_in_use(self, hostname):
        try:
            socket.getaddrinfo(hostname, 0)
            return True
        except:
            return False

    def api_gateway_check(self, all_domains: list, domain: str) -> dict:
        if domain in all_domains or domain[:-1] in all_domains:
            return {"type": 'good', "message": "API Gateway owned by account"}
        elif not self.gateway_in_use(domain):
            return {"type": 'issue', "message": "API Gateway does not exist"}
        else:
            return {"type": 'warning', "message": "API Gateway owned by another account"}
