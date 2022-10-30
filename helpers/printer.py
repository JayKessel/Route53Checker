

class Printer:
    def __init__(self):
        self.suppress = False

    def print_resource_result(self, domain, results, affected_resource):
        if results['type'] == 'issue':
            print(f"\033[91mIssue {domain} - {results['message']} - {affected_resource}")
        elif results['type'] == 'warning' and not self.suppress:
            print(f"\033[93mWarning {domain} - {results['message']} - {affected_resource}")
        return dict(domain=domain, message=results['message'], record=affected_resource,
                    type=results['type'])

    def display(self, message):
        print(message)

    def output_message(self):
        output = "outputs data to a file in JSON format"
        return output

    def suppress_message(self):
        suppress = "supresses findings that are warnings"
        return suppress

    def domain_message(self):
        domain = "finds dangling domains unrelated to the supplied checks"
        return domain

    def checks_message(self):
        checks = """determines which checks to perform. 
        Use 'all' to perform all checks.
         For specific checks, use any of the following (comma separated, without spaces).
        s3, apigateway, cloudfront, elasticbeanstalk, loadbalancer, ec2
        """
        return checks

    def main_message(self):
        message = """
 _____             _         _____ ____     _____ _               _             
|  __ \           | |       | ____|___ \   / ____| |             | |            
| |__) |___  _   _| |_ ___  | |__   __) | | |    | |__   ___  ___| | _____ _ __ 
|  _  // _ \| | | | __/ _ \ |___ \ |__ <  | |    | '_ \ / _ \/ __| |/ / _ \ '__|
| | \ \ (_) | |_| | ||  __/  ___) |___) | | |____| | | |  __/ (__|   <  __/ |   
|_|  \_\___/ \__,_|\__\___| |____/|____/   \_____|_| |_|\___|\___|_|\_\___|_|   

The all in one Route 53 issue identifier.
"""
        print(message)
