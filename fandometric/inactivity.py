from datetime import datetime

from .indie import get_record, to_url_set
from .output import white, fail, bold, succ, graybg, blackbg

def _format_following(following, mutuals):
    mutuality_key = (('', '—'), (succ, 'mutual'))
    altern = (blackbg, graybg)
    for i, (url, t) in enumerate(sorted(following, key=lambda k: k[1], reverse=True)):
        bg = altern[i % 2]
        mcolor, mtext = mutuality_key[url in mutuals]
        yield (32, -1, bg + white, datetime.fromtimestamp(t).strftime('%B %d, %Y at %I:%M %p')), (10, 0, mcolor + bg, mtext), (8, 0, bg + white, str(i)), (33, -1, bold + bg + white, url), (60, -1, bg + white, 'http://tumblr.com/unfollow/' + url)

def listfollowing(directory, a):
    T, followers, following = get_record(directory, a)
    return _format_following(following, to_url_set(followers))

