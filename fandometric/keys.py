from . import pytumblr
from . import authorize

def get_keys():
    with open('tumblr_keys.txt', 'rb') as K:
        keys = [l.decode().strip() for l in K.readlines() if l][:4]
    return keys

try:
    _keys = get_keys()
except FileNotFoundError:
    _keys = ()
if len(_keys) != 4:
    authorize.setup()
    _keys = get_keys()
client = pytumblr.TumblrRestClient( * _keys )
