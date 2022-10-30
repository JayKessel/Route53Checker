import logging

import boto3
from botocore.exceptions import ClientError


class s3Check:
    def __init__(self, logging):
        self.logging = logging
        self.session = boto3.session.Session()
        self.s3_client = boto3.client('s3')

    def s3_check(self, buckets: list, domain: str) -> dict:
        """ Route 53 S3 bucket checker """
        if domain in buckets:
            return {"type": 'good', "message": "bucket owned by account"}
        if self.bucket_exists(domain):
            return {"type": 'warning', "message": "bucket owned by another account"}
        else:
            return {"type": 'issue', "message": "bucket name unclaimed"}

    def get_buckets(self) -> list:
        """ Returns a list of S3 buckets associated with the account """
        buckets = []
        try:
            response = self.s3_client.list_buckets()
            for bucket in response['Buckets']:
                buckets.append(
                    bucket["Name"].lower()
                )
        except Exception as e:
            self.logging.error(f"Couldn't get buckets for account - {str(e)}")
        self.logging.debug(buckets)
        self.logging.info("Buckets for account returned")
        return buckets

    def bucket_exists(self, bucket_name: str) -> bool:
        """ Determines whether the given bucket exists """
        try:
            response = self.s3_client.head_bucket(
                Bucket=bucket_name
            )
            logging.debug(response)
        except ClientError as e:
            if e.response['Error']['Code'] == '404':
                return False
            elif e.response['Error']['Code'] == '403':
                return True
            else:
                return False
        except Exception as e:
            print(str(e))
            self.logging.error(f"Couldn't determine if bucket exists - {str(e)}")
            return False
        return True
