import time
from httplib2 import ServerNotFoundError
from ssl import CertificateError

from .keys import client

def pause(seconds, message):
    units = 'second', 'seconds'
    for s in range(seconds, 0, -1):
        yield message.format(s, unit=units[seconds != 1])
        time.sleep(1)
        
def yield_users(func, field, * args):
    count = 0
    
    while True:
        try:
            blogs = func( * args, limit=20, offset=count)
        except ServerNotFoundError:
            yield from pause(4, 'Server not found (retry in {0} {unit})')
            continue

        if field in blogs and blogs[field]:
            yield from blogs[field]
            count += len(blogs[field])

        elif 'meta' in blogs and 'status' in blogs['meta']:
            yield from pause(10, 'Rate limit hit (retry in {0} {unit})')
        
        else:
            break

def exists(url):
    try:
        if "meta" in client.blog_info(url) and "status" in client.blog_info(url)["meta"]:
            if client.blog_info(url)["meta"]["status"] == 404:
                return 0
            else:
                print (url + " [other error?]")
                return 0
        else:
            return 1
    except (CertificateError, ServerNotFoundError):
        return 2
