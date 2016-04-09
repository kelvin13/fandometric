import time

from .fetch import yield_users
from .track import check
from .inactivity import listfollowing
from .output import render_table
from .indie import write_record, max_file_index
from .keys import client

def update(url, directory='records'):
    followers = [U['name'] + '|' + str(U['updated']) for U in yield_users(client.followers, 'users', url)]
    following = [U['name'] + '|' + str(U['updated']) for U in yield_users(client.following, 'blogs')]

    write_record(time.time(), followers, following, directory)

def compare(a=None, b=None, directory='records'):
    if a is None:
        a = 0
    if b is None:
        b = a
    b, a = sorted((abs(a), abs(b)))
    n = max_file_index(directory)
    print(render_table( * check(directory, n - a, n - b) ))

def changes(url, * args, ** kwargs ):
    update(url, ** kwargs )
    compare( * args, ** kwargs )

def following(a=None, directory='records'):
    if a is None:
        a = 0
    n = max_file_index(directory)
    print(render_table( listfollowing(directory, n - a) ))
