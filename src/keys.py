from . import pytumblr
from . import authorize

def _get_keys():
    with open('tumblr_keys.txt', 'rb') as K:
        keys = [l.decode().strip() for l in K.readlines() if l][:4]
    return keys

def make_client():
    try:
        _keys = _get_keys()
    except FileNotFoundError:
        _keys = ()
    if len(_keys) == 4:
        return pytumblr.TumblrRestClient( * _keys )
    else:
        return None

client = None
