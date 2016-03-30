import time

from . import fetch
from . import indie
from . import track
from .indie import max_file_index
from .keys import client

def update(url, directory='records'):
    followers = [U['name'] + '|' + str(U['updated']) for U in fetch.yield_users(client.followers, 'users', url)]
    following = [U['name'] + '|' + str(U['updated']) for U in fetch.yield_users(client.following, 'blogs')]

    indie.write_record(time.time(), followers, following, directory)

def compare(a=None, b=None, directory='records'):
    if a is None:
        a = 0
    if b is None:
        b = a
    b, a = sorted((abs(a), abs(b)))
    n = max_file_index(directory)
    print(track.render_table( * track.check(directory, n - a, n - b) ))

def changes(url, * args, ** kwargs ):
    update(url, ** kwargs )
    compare( * args, ** kwargs )
