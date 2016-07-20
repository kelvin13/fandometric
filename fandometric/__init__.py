import time

from . import nest

from .fetch import yield_users
from .track import check
from .inactivity import listfollowing
from .output import render_table, invert, succ, warning, endc
from .indie import write_record, max_file_index
from .keys import client

def _get_total_followers(url):
    while True:
        try:
            return client.followers(url, limit=0)['total_users']
        except KeyError:
            pass

def _get_total_following():
    while True:
        try:
            return client.info()['user']['following']
        except KeyError:
            pass

def _format_status(status, limit):
    return '{0: <{fill}}{end}'.format(status, fill=limit, end=endc)
    
def _get_users(get_total, * args , search=None, search_ui='[{0}]'):
    if search is not None:
        search_status = False
        search_string = search_ui.format('x')
    
    print(succ, 'Connecting to tumblr...', end=endc)
    total = get_total( * args[2:] )
    n = 0
    
    limit = 56
    bar_length = 16
    for U in yield_users( * args ):
        if type(U) is str:
            status = _format_status(warning + U, limit)
            if search is None:
                status = status,
            else:
                status = search_string, status
        else:
            status = _format_status(succ + 'Fetching blogs ({0} of {1})'.format(n, total), limit)

            if search is None:
                status = status,
            else:
                if not search_status and search(U):
                    search_status = True
                    search_string = invert + search_ui.format('+') + endc
                status = search_string, status
            
            n += 1
            yield U
        chunks = int(round(bar_length * n / total))
        print('\r', '[' + '█'*chunks + ' '*(bar_length - chunks) + ']', * status, end='')
        
    print()

def _serialize(UU):
    return ((U['name'] + '|' + str(U['updated']) for U in UU))

def update(url, directory='records'):
    following = _get_users(_get_total_following, client.following, 'blogs')
    followers = _get_users(_get_total_followers, client.followers, 'users', url, search=lambda U: type(U) is dict and U['name'] == 'taylorswift', search_ui='[{0} TAYLOR]')
    
    write_record(time.time(), _serialize(followers), _serialize(following), directory)

def compare(a=None, b=None, directory='records'):
    if a is None:
        a = 0
    if b is None:
        b = a
    
    n = max_file_index(directory)
    a, b = sorted((n - abs(a), n - abs(b)))
    
    print(succ, 'Checking blog movement between records {0} and {1}...'.format(a, b), endc, end='\n\n')
    try:
        tablecontents = check(directory, a, b)
    except FileNotFoundError as message:
        if n <= 1:
            print(' Comparisons require more than one snapshot. Please try running fandometric.update again later.')
        else:
            print(message)
    else:
        print(render_table( * tablecontents ))

def changes(url, * args, ** kwargs ):
    update(url, ** kwargs )
    compare( * args, ** kwargs )

def following(a=None, directory='records'):
    if a is None:
        a = 0
    n = max_file_index(directory)
    print(render_table( listfollowing(directory, n - a) ))
