MESSAGE = """
  _____             _         _____ ____     _____ _               _             
 |  __ \           | |       | ____|___ \   / ____| |             | |            
 | |__) |___  _   _| |_ ___  | |__   __) | | |    | |__   ___  ___| | _____ _ __ 
 |  _  // _ \| | | | __/ _ \ |___ \ |__ <  | |    | '_ \ / _ \/ __| |/ / _ \ '__|
 | | \ \ (_) | |_| | ||  __/  ___) |___) | | |____| | | |  __/ (__|   <  __/ |   
 |_|  \_\___/ \__,_|\__\___| |____/|____/   \_____|_| |_|\___|\___|_|\_\___|_|   
                                                                                 
                                                                                                                                                    
--help (-h) displays this message

Use the following to perform all checks:
--checks (-c) all -d

Alternatively you may select specific checks. These should be comma separated.
--checks (-c) s3

The following checks are available:

s3, apigateway, cloudfront, elasticbeanstalk, loadbalancer, ec2, domain

Find dangling domains unrelated to the supplied checks using the following:
--domain (-d)

Suppress warnings:
--suppress (-s)

Output data to a file in JSON format:
--output (-o) [filename]

"""


def main_message():
    print(MESSAGE)


def print_resource_result(domain, results, affected_resource):
    if results['type'] == 'issue':
        print(f"\033[91mIssue {domain} - {results['message']} - {affected_resource}")
    elif results['type'] == 'warning':
        print(f"\033[93mWarning {domain} - {results['message']} - {affected_resource}")


def display(message):
    print(message)


class Printer:
    def __init__(self, logging):
        self.logging = logging
