from itertools import chain
from ssl import CertificateError
from httplib2 import ServerNotFoundError

from .keys import client

_fail = '\033[91m'
_bold = '\033[1m'
_endc = '\033[0m'
_succ = '\033[92m'

def mono_align(width, align, color, text):
    if align:
        if align == 1:
            return color, ('{:>' + str(width) + '}').format(text), _endc
        else:
            return color, ('{:<' + str(width) + '}').format(text), _endc
    else:
        return color, ('{:^' + str(width) + '}').format(text), _endc
def render_table( * tables ):
    cfi = chain.from_iterable
    return '\n'.join(cfi((''.join(cfi(mono_align( * cell ) for cell in row)) for row in table) for table in tables))

def get_record(directory, N):
    with open(directory + '/' + str(N) + '.txt', 'r') as F:
        followers, following = F.read().split('~~~')
        T, * followers = followers.split()
        followers = [(url, float(t)) for url, t in (blog.split('|') for blog in followers)]
        following = [(url, float(t)) for url, t in (blog.split('|') for blog in following.split())]
        return float(T), followers, following

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

def to_url_set(blogs):
    return set(U[0] for U in blogs)

def blog_difference(blogs, SET, func):
    for url, t in blogs:
        if url not in SET:
            yield func(url, t)

def inactive(T, blogs, threshold):
    return (blog for blog in blogs if T - blog[1] > threshold)

def percent(a, b, roundto=5, desc='', noun=('', '')):
    if desc:
        desc = ' ' + desc
    noun = tuple(' ' + case if case else '' for case in noun)
    try:
        p = round(a/b * 100, roundto)
    except ZeroDivisionError:
        p = 'undefined '
    return ''.join((str(p), '% ', desc, ' (', str(a), noun[p != 1], ')'))

def stats(T, followers, following):
    threshold = 604800
    inactive_following = tuple(inactive(T, following, threshold))
    inactive_followers = tuple(inactive(T, followers, threshold))
    try:
        ratio = round(len(followers)/len(following), 5)
    except ZeroDivisionError:
        ratio = 'undefined'
    return [((_bold, 'ratio = ' + str(ratio)), ('', '(' + str(len(followers)) + ':' + str(len(following)) + ')')),
            (('', percent(len(inactive_following), len(following), desc='inactive following', noun=('blog', 'blogs'))),),
            (('', percent(len(inactive_followers), len(followers), desc='inactive followers', noun=('blog', 'blogs'))),)]

def show_count(L, noun=('', '')):
    n = len(L)
    return 1, -1, _bold, ' '.join((str(n), noun[n != 1]))

state_key = {0: (_fail, 'deleted'), 1: ('', 'exists'), 2: ('', 'unknown'), 3: (_succ, 'new')}
def format_lost_followers(lost):
    lost = tuple(lost)
    yield (show_count(lost, ('lost follower', 'lost followers')),)
    mutuality_key = (('', '—'), (_fail + _bold, 'mutual'))
    for state, mutuality, url, link in lost:
        yield (13, 0) + state_key[state], (13, 0) + mutuality_key[mutuality], (32, -1, '', url), (44, -1, '', link)

def format_gained_followers(gained):
    gained = tuple(gained)
    yield (show_count(gained, ('gained follower', 'gained followers')),)
    mutuality_key = (('', '—'), (_succ, 'mutual'))
    for state, mutuality, url, link in gained:
        yield (13, 0) + state_key[state], (13, 0) + mutuality_key[mutuality], (32, -1, '', url), (44, -1, '', link)

def format_cells(additional):
    for cells in additional:
        yield ((22, -1) + cell for cell in cells)
    
def check(directory, a, b):
    T1, old_followers, old_following = get_record(directory, a)
    T2, current_followers, current_following = get_record(directory, b)
    
    current_following_urls = to_url_set(current_following)
    current_followers_urls = to_url_set(current_followers)
    old_followers_urls = to_url_set(old_followers)
    # 0-Deleted, 1-Exists, 2-Unknown, 3-New
    
    def is_mutual(url):
        return url in current_following_urls
    
    lost = blog_difference(old_followers, current_followers_urls, lambda url, t: (exists(url), is_mutual(url), url, 'http://' + url + '.tumblr.com'))
    gained = blog_difference(current_followers, old_followers_urls, lambda url, t: (3, is_mutual(url), url, 'http://' + url + '.tumblr.com'))
    return (format_lost_followers(lost),
                format_gained_followers(gained),
                format_cells(stats(T2, current_followers, current_following)))
