import socket


class Domain:
    """ Checks for dangling domains in Route 53 records """
    def __init__(self, logging):
        self.logging = logging

    def in_use(self, hostname):
        try:
            socket.getaddrinfo(hostname, 0)
            return True
        except:
            return False

    def domain_check(self, domain: str) -> dict:
        if not self.in_use(domain):
            return {"type": 'issue', "message": "No DNS entry for domain"}
        else:
            return {"type": 'good', "message": "Domain exists"}
