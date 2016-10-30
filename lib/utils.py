import requests
import re
import certifi
from netifaces import ifaddresses
from sh import grep, netstat
from urlparse import urlparse
import pytz

HTTP_OK = xrange(200, 299)

def validate_url(string):
    """Simple URL verification.
    >>> validate_url("hello")
    False
    >>> validate_url("ftp://example.com")
    False
    >>> validate_url("http://")
    False
    >>> validate_url("http://wireload.net/logo.png")
    True
    >>> validate_url("https://wireload.net/logo.png")
    True
    """

    checker = urlparse(string)
    return bool(checker.scheme in ('http', 'https') and checker.netloc)

def url_fails(url):
    """
    Try HEAD and GET for URL availability check.
    """

    # Use Certifi module
    verify = certifi.where()

    headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Linux armv7l) AppleWebKit/538.15 (KHTML, like Gecko) Version/8.0 Safari/538.15',
    }
    try:
        if not validate_url(url):
            return False

        if requests.head(
            url,
            allow_redirects=True,
            headers=headers,
            timeout=10,
            verify=verify
        ).status_code in HTTP_OK:
            return False

        if requests.get(
            url,
            allow_redirects=True,
            headers=headers,
            timeout=10,
            verify=verify
        ).status_code in HTTP_OK:
            return False

    except (requests.ConnectionError, requests.exceptions.Timeout):
        pass

    return True
