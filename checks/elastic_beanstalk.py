import boto3
import socket


class ElasticBeanstalk:
    """ Checks Elastic Beanstalk resources in Route 53 records """
    def __init__(self, logging):
        self.logging = logging
        self.regions = boto3.session.Session().get_available_regions('elasticbeanstalk')

    def get_endpoints(self, region: str) -> list:
        next_token = ''
        returned_urls = []
        self.elasticbeanstalk_client = boto3.client('elasticbeanstalk', region_name=region)
        try:
            response = self.elasticbeanstalk_client.describe_environments(
                MaxRecords=100
            )
            for item in response['Environments']:
                returned_urls.append(item['EndpointURL'].lower())
                returned_urls.append(item['CNAME'].lower())
            if 'NextToken' in list(response.keys()):
                next_token = response['NextToken']
        except Exception as e:
            self.logging.warning(f"Boto3 responded with an error - {str(e)}")
        while next_token != '':
            try:
                response = self.elasticbeanstalk_client.describe_environments(
                    MaxRecords=100,
                    NextToken=next_token
                )
                for item in response['Environments']:
                    returned_urls.append(item['EndpointURL'].lower())
                    returned_urls.append(item['CNAME'].lower())
                if 'NextToken' in list(response.keys()):
                    next_token = response['NextToken']
                else:
                    next_token = ''
            except Exception as e:
                self.logging.error(f"Boto3 responded with an error - {str(e)}")
                break

        return returned_urls

    def get_all_endpoints(self) -> list:
        all_urls = []
        for region in self.regions:
            all_urls += self.get_endpoints(region)
        return all_urls

    def gateway_in_use(self, hostname):
        try:
            socket.getaddrinfo(hostname, 0)
            return True
        except:
            return False

    def elastic_beanstalk_check(self, all_domains: list, domain: str) -> dict:
        if domain in all_domains or domain[:-1] in all_domains:
            return {"type": 'good', "message": "Elastic Beanstalk owned by account"}
        elif not self.gateway_in_use(domain):
            return {"type": 'issue', "message": "Elastic Beanstalk does not exist"}
        else:
            return {"type": 'warning', "message": "Elastic Beanstalk owned by another account"}
