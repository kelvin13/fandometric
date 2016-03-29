from itertools import chain
from ssl import CertificateError
from httplib2 import ServerNotFoundError

from .tumblr_keys import client

_fail = '\033[91m'
_bold = '\033[1m'
_endc = '\033[0m'
_succ = '\033[92m'

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

def inactive(T, blogs, roundto=5):
    count = sum(T - U[1] > 604800 for U in blogs)
    try:
        percent = round(count/len(blogs) * 100, roundto)
    except ZeroDivisionError:
        percent = 'undefined'
    return count, percent

def stats(T, followers, following):
    inactive_following = inactive(T, following)
    inactive_followers = inactive(T, followers)
    try:
        ratio = round(len(followers)/len(following), 5)
    except ZeroDivisionError:
        ratio = 'undefined'
    return [((_bold, 'ratio = ' + str(ratio)), ('', '(' + str(len(followers)) + ':' + str(len(following)) + ')')),
            (('', str(inactive_following[1]) + '% inactive following (' + str(inactive_following[0]) + ' blogs)'),),
            (('', str(inactive_followers[1]) + '% inactive followers (' + str(inactive_followers[0]) + ' blogs)'),)]

def to_url_set(blogs):
    return set(U[0] for U in blogs)

def lost_followers(old_followers, current_followers_urls, current_following_urls):
    for url, t in old_followers:
        if url not in current_followers_urls:
            yield exists(url), url in current_following_urls, url, 'http://' + url + '.tumblr.com'

def gained_followers(current_followers, old_followers_urls, current_following_urls):
    for url, t in current_followers:
        if url not in old_followers_urls:
            yield 3, url in current_following_urls, url, 'http://' + url + '.tumblr.com'
    
def check(directory, a, b):
    T1, old_followers, old_following = get_record(directory, a)
    T2, current_followers, current_following = get_record(directory, b)
    
    current_following_urls = to_url_set(current_following)
    current_followers_urls = to_url_set(current_followers)
    old_followers_urls = to_url_set(old_followers)
    # 0-Deleted, 1-Exists, 2-Unknown, 3-New
    
    return build_table(lost_followers(old_followers, current_followers_urls, current_following_urls),
                    gained_followers(current_followers, old_followers_urls, current_following_urls),
                    stats(T2, current_followers, current_following))

def build_table(lost, gained, additional):
    state_key = {0: (_fail, 'deleted'), 1: ('', 'exists'), 2: ('', 'unknown'), 3: (_succ, 'new')}
    mutuality_key = (('', '—'), (_fail + _bold, 'mutual'))
    for state, mutuality, url, link in lost:
        yield (13, 0) + state_key[state], (13, 0) + mutuality_key[mutuality], (32, -1, '', url), (44, -1, '', link)

    mutuality_key = (('', '—'), (_succ, 'mutual'))
    for state, mutuality, url, link in gained:
        yield (13, 0) + state_key[state], (13, 0) + mutuality_key[mutuality], (32, -1, '', url), (44, -1, '', link)

    for cells in additional:
        yield ((22, -1) + cell for cell in cells)

def mono_align(width, align, color, text):
    if align:
        if align == 1:
            return color, ('{:>' + str(width) + '}').format(text), _endc
        else:
            return color, ('{:<' + str(width) + '}').format(text), _endc
    else:
        return color, ('{:^' + str(width) + '}').format(text), _endc
def render_table(table):
    cfi = chain.from_iterable
    return '\n'.join(''.join(cfi(mono_align( * cell ) for cell in row)) for row in table)
