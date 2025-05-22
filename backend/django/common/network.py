"""
Some useful classes / functions for network infos
"""

PRIVATE_IPS_PREFIX = ('10.', '172.', '192.', )

def get_client_ip(request):
    """
    Return the client public ip from a request
    """
    ip = request.META.get('REMOTE_ADDR')
    # Try to get the first non-proxy ip (not a private ip) from the HTTP_X_FORWARDED_FOR
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        proxies = x_forwarded_for.split(',')
        # Remove the private ips from the beginning
        while (len(proxies) > 0 and proxies[0].startswith(PRIVATE_IPS_PREFIX)):
            proxies.pop(0)
        # Take the first ip which is not a private one (of a proxy)
        if len(proxies) > 0:
            ip = proxies[0].strip()
    # Possibly None ip
    return ip