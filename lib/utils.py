import requests
import re
from netifaces import ifaddresses
from sh import grep, netstat
from urlparse import urlparse
from os import environ
import sys
import sh
import hashlib
import os

HTTP_OK = xrange(200, 299)

def validate_url(string):
    checker = urlparse(string)
    return bool(checker.scheme in ('http', 'https', 'rtsp', 'rtmp') and checker.netloc)


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


def file_get_contents(filename):
    if os.path.exists(filename):
        fp = open(filename, "r")
        content = fp.read()
        fp.close()
        return content.rstrip()

def is_debugging():
    return "/mnt" in os.getcwd() or "DEBUG" in os.environ
