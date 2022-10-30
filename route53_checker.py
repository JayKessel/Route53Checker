import sys
import logging
import validators

from checks.s3 import s3Check
from checks.api_gateway import APIGateway
from checks.cloudfront import Cloudfront
from checks.elastic_beanstalk import ElasticBeanstalk
from checks.loadbalancer import Loadbalancer
from checks.domain import Domain
from checks.ec2 import EC2
from helpers.route53 import route53
import helpers.printer as printer

LOGGING_LEVEL = logging.ERROR

root = logging.getLogger()
root.setLevel(LOGGING_LEVEL)
handler = logging.StreamHandler(sys.stdout)
handler.setLevel(LOGGING_LEVEL)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
root.addHandler(handler)

all_checks = ["s3", "apigateway", "cloudfront", "elasticbeanstalk", "loadbalancer", "ec2", "domain"]

if __name__ == "__main__":
    arguments = sys.argv
    if len(arguments) != 3:
        printer.main_message()
        sys.exit(0)
    checks = arguments[2].split(",")
    if len(checks) == 0:
        printer.main_message()
        sys.exit(1)
    if checks[0] == 'all':
        checks = all_checks[:-1]
    if not set(checks).issubset(set(all_checks)):
        printer.main_message()
        sys.exit(1)

    printer.display("Starting ingestion for the following resources")
    printer.display(" ".join(checks))

    printer.display("Route53 Ingestion")
    route53 = route53(root)
    hosted_zone_ids = route53.get_hosted_zone_ids()
    buckets = None
    s3 = None
    apigateway = None
    apigateways = None
    cloudfront = None
    cloudfronts = None
    elasticbeanstalk = None
    elasticbeanstalks = None
    loadbalancer = None
    loadbalancers = None
    ec2 = None
    ec2s = None
    domain = None

    if 's3' in checks:
        printer.display("S3 Ingestion")
        s3 = s3Check(root)
        buckets = s3.get_buckets()
    if 'apigateway' in checks:
        printer.display("API Gateway Ingestion")
        apigateway = APIGateway(root)
        apigateways = apigateway.get_all_endpoints()
    if 'cloudfront' in checks:
        printer.display("Cloudfront Ingestion")
        cloudfront = Cloudfront(root)
        cloudfronts = cloudfront.get_distributions()
    if 'elasticbeanstalk' in checks:
        printer.display("Elastic Beanstalk Ingestion")
        elasticbeanstalk = ElasticBeanstalk(root)
        elasticbeanstalks = elasticbeanstalk.get_all_endpoints()
    if 'loadbalancer' in checks:
        printer.display("Loadbalancer Ingestion")
        loadbalancer = Loadbalancer(root)
        loadbalancers = loadbalancer.get_all_loadbalancers()
    if 'ec2' in checks:
        printer.display("EC2 Ingestion")
        ec2 = EC2(root)
        ec2s = ec2.get_all_ec2_domains_and_ips()
    if 'domain' in checks:
        domain = Domain(root)

    results = []
    printer.display("Parsing results")
    for hosted_zone_id in hosted_zone_ids:
        all_zone_infos = route53.get_hosted_zone_records(hosted_zone_id)
        for all_zone_info in all_zone_infos:
            if all_zone_info["type"] == 'A' or all_zone_info["type"] == 'CNAME':
                for record in all_zone_info["records"]:
                    if not record.endswith("."):
                        record += "."
                    if 's3' in checks:
                        if record.startswith("s3-website.") and record.endswith(f".amazonaws.com."):
                            check_bucket = s3.s3_check(buckets, all_zone_info['name'][:-1])
                            printer.print_resource_result(all_zone_info['name'][:-1], check_bucket, record)
                            continue
                    if 'apigateway' in checks:
                        if ".execute-api." in record and record.endswith(f".amazonaws.com."):
                            check_apigateway = apigateway.api_gateway_check(apigateways, record)
                            printer.print_resource_result(all_zone_info['name'][:-1], check_apigateway, record)
                            continue
                    if 'cloudfront' in checks:
                        if record.endswith(f".cloudfront.net."):
                            check_cloudfront = cloudfront.cloudfront_check(cloudfronts, record)
                            printer.print_resource_result(all_zone_info['name'][:-1], check_cloudfront, record)
                            continue
                    if 'elasticbeanstalk' in checks:
                        if record.endswith(f".elasticbeanstalk.com."):
                            check_elasticbeanstalk = elasticbeanstalk.elastic_beanstalk_check(
                                elasticbeanstalks, record)
                            printer.print_resource_result(all_zone_info['name'][:-1],
                                                          check_elasticbeanstalk, record)
                            continue
                    if 'loadbalancer' in checks:
                        if record.endswith(f".elb.amazonaws.com."):
                            check_loadbalancer = loadbalancer.loadbalancercheck(loadbalancers,
                                                                                record.replace(
                                                                                    "dualstack.",
                                                                                    ""))
                            printer.print_resource_result(all_zone_info['name'][:-1],
                                                          check_loadbalancer, record)
                            continue
                        if record.endswith(f".amazonaws.com.") and ".elb." in record:
                            check_loadbalancer = loadbalancer.loadbalancercheck(loadbalancers,
                                                                                record.replace(
                                                                                    "dualstack.", ""))
                            printer.print_resource_result(all_zone_info['name'][:-1],
                                                          check_loadbalancer, record)
                            continue
                    if 'ec2' in checks:
                        if record.endswith(".compute.amazonaws.com."):
                            check_ec2 = ec2.ec2check(ec2s, record)
                            printer.print_resource_result(all_zone_info['name'][:-1], check_ec2,
                                                          record)
                    if 'domain' in checks:
                        if validators.domain(record[:-1]):
                            check_domain = domain.domain_check(record[:-1])
                            printer.print_resource_result(all_zone_info['name'][:-1], check_domain, record)

