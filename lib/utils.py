import requests
import re
import certifi
from netifaces import ifaddresses
from sh import grep, netstat
from urlparse import urlparse
import pytz
import sys
import sh
import hashlib

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

def download_with_progress(file_name, url):
    with open(file_name, "wb") as f:
        print "Downloading %s" % file_name
        response = requests.get(url, stream=True)
        total_length = response.headers.get('content-length')

        if total_length is None: # no content length header
            f.write(response.content)
        else:
            dl = 0
            total_length = int(total_length)
            for data in response.iter_content(chunk_size=4096):
                dl += len(data)
                f.write(data)
                done = int(50 * dl / total_length)
                sys.stdout.write("\r[%s%s]" % ('=' * done, ' ' * (50-done)) )
                sys.stdout.flush()

def get_git_tag():
    commit = sh.git("rev-list", "--tags", "--max-count=1").rstrip()
    return sh.git("describe", "--tags", commit).rstrip()


def md5(fname):
    hash_md5 = hashlib.md5()
    with open(fname, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()
