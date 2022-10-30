import boto3
import sys


class route53:
    def __init__(self, logging):
        self.logging = logging
        # Route 53 only has one region (us-east-1)
        self.route53_client = boto3.client('route53', region_name='us-east-1')

    def get_hosted_zone_ids(self) -> list:
        """ Retrieves a list of all hosted IDs for an AWS account """
        all_records = False
        returned_hosted_zone_ids = []
        marker = ''
        while not all_records:
            try:
                if marker != '':
                    response = self.route53_client.list_hosted_zones(
                        MaxItems='100',
                        Marker=marker
                    )
                else:
                    response = self.route53_client.list_hosted_zones(
                        MaxItems='100'
                    )
                self.logging.info("get_hosted_zones responded")
                self.logging.debug(str(response))
            except Exception as e:
                self.logging.error(f"Boto3 responded with an error - {str(e)}")
                sys.exit(1)
            if 'HostedZones' in list(response.keys()):
                for hosted_zone in response['HostedZones']:
                    returned_hosted_zone_ids.append(hosted_zone['Id'])
            else:
                self.logging.error(f"Unknown response format received from get_hosted_zones")
            if 'NextMarker' in list(response.keys()):
                marker = response['NextMarker']
            else:
                all_records = True
        self.logging.info("get_hosted_zone_ids returned")
        self.logging.debug(returned_hosted_zone_ids)
        return returned_hosted_zone_ids

    def get_hosted_zone_records(self, hosted_zone_id: str) -> list:
        """ Retrieves a list of all records for a given host ID """
        all_records = False
        returned_hosted_zone_info = []
        start_record_name = ''
        start_record_type = ''
        start_record_identifier = ''
        while not all_records:
            try:
                if start_record_identifier != '':
                    response = self.route53_client.list_resource_record_sets(
                        HostedZoneId=hosted_zone_id,
                        MaxItems='100',
                        StartRecordName=start_record_name,
                        StartRecordType=start_record_type,
                        StartRecordIdentifier=start_record_identifier,
                    )
                elif start_record_name != '':
                    response = self.route53_client.list_resource_record_sets(
                        HostedZoneId=hosted_zone_id,
                        MaxItems='100',
                        StartRecordName=start_record_name,
                        StartRecordType=start_record_type
                    )
                else:
                    response = self.route53_client.list_resource_record_sets(
                        HostedZoneId=hosted_zone_id,
                        MaxItems='100'
                    )
                self.logging.info("list_resource_record_sets responded")
                self.logging.debug(str(response))
            except Exception as e:
                self.logging.error(f"Boto3 responded with an error - {str(e)}")
                sys.exit(1)
            if 'ResourceRecordSets' in list(response.keys()):
                for record in response['ResourceRecordSets']:
                    record_keys = list(record.keys())
                    data = []
                    if 'ResourceRecords' in record_keys:
                        for instance in record['ResourceRecords']:
                            data.append(instance['Value'])
                    elif 'AliasTarget' in record_keys:
                        data.append(record['AliasTarget']['DNSName'])
                    returned_hosted_zone_info.append({
                        "name": record['Name'],
                        "type": record['Type'],
                        "records": data
                    })
            else:
                self.logging.error(f"Unknown response format received from list_resource_record_sets")
            if 'NextRecordName' in list(response.keys()):
                start_record_name = response['NextRecordName']
                start_record_type = response['NextRecordType']
                if 'NextRecordIdentifier' in list(response.keys()):
                    start_record_identifier = response['NextRecordIdentifier']
            else:
                all_records = True
        self.logging.info("get_hosted_zone_ids returned")
        self.logging.debug(returned_hosted_zone_info)
        return returned_hosted_zone_info
