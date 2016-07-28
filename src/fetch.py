from httplib2 import ServerNotFoundError
from ssl import CertificateError

from . import keys, ui

def pause(seconds, message):
    units = 'second', 'seconds'
    message += ' (retry in {s} {unit})'
    for s in range(seconds, 0, -1):
        yield message.format(s=s, unit=units[s != 1])
        ui.sleep(1)
        
def yield_users(url):
    if url is None:
        func  = keys.client.following
        field = 'blogs'
        args = ()
    else:
        func  = keys.client.followers
        field = 'users'
        args = url,
    
    count = 0
    
    while True:
        try:
            blogs = func( * args, limit=20, offset=count)
        except ServerNotFoundError:
            yield from pause(4, 'Server not found')
            continue

        if field in blogs and blogs[field]:
            yield from blogs[field]
            count += len(blogs[field])
            ui.sleep(0.005)

        elif 'meta' in blogs and 'status' in blogs['meta']:
            yield from pause(10, 'Rate limit hit')
        
        else:
            break

def attempt_api_call(out, func, * args, ** kwargs ):
    while True:
        Q = func( * args, ** kwargs )
        if 'meta' in Q and Q['meta']['status'] == 500:
            for message in pause(3, 'Tumblr server error'):
                out({'color': 'warning', 'msg': message + ' '})
        else:
            return Q

def exists(url):
    try:
        R = keys.client.blog_info(url)
        if 'meta' in R and 'status' in R['meta']:
            if R['meta']['status'] == 404:
                return 0
            else:
                print (url + ' [other error?]')
                return 0
        else:
            return 1
    except (CertificateError, ServerNotFoundError):
        return 2
